from easy.ast import FuncDefinition, IdExpr
from easy.type import Type
from easy.visitors.base import BaseVisitor

def error(msg, a=None, b=None):
    print msg

    lines = None
    if a and b:
        lines = (min(a.lineno_between + b.lineno_between), max(a.lineno_between + b.lineno_between))
    elif a:
        lines = a.lineno_between

    if lines is not None:
        if lines[0] == lines[1]:
            print 'Somewhere on line %d' % lines[0]
        else:
            print 'Somewhere between lines %d-%d' % lines

    exit(1)

class NewLexicalScope(object):
    def __init__(self, visitor, node):
        self._visitor = visitor
        self._node = node

    def __enter__(self):
        self._visitor._cur_table = SymbolTable(self._visitor._cur_table)
        self._node.symtable = self._visitor._cur_table

    def __exit__(self, *args):
        self._visitor._cur_table = self._visitor._cur_table.parent

class SymbolTable(dict):
    def __init__(self, parent=None):
        if parent is None:
            parent = {
                'puts': FuncDefinition('puts', [IdExpr('_', 'String')], [], 'Void'),
                'atoi': FuncDefinition('atoi', [IdExpr('_', 'String')], [], 'Number'),
                'printf': FuncDefinition('printf', [], [], 'Void'),
            }
        self.parent = parent
        self.num_variables = 0
        self.var_idx = {}

    def __contains__(self, key):
        if self.has_key(key):
            return True
        return key in self.parent

    def __getitem__(self, key):
        if self.has_key(key):
            return self.get(key)
        return self.parent[key]

    def __str__(self):
        ret = repr(self)
        if self.parent:
            ret += ' / ' + str(self.parent)
        return ret

    def add(self, symbol, node):
        if symbol in self:
            error("Identifier name already in use: '%s'" % symbol, node)
        self[symbol] = node

        if isinstance(node, IdExpr):
            self.var_idx[symbol] = self.num_variables
            self.num_variables += 1

    def find(self, symbol):
        obj = self
        while not obj.has_key(symbol):
            obj = obj.parent
        return obj

class SymbolTableVisitor(BaseVisitor):
    def __init__(self, *args, **kwargs):
        super(SymbolTableVisitor, self).__init__(*args, **kwargs)
        self._cur_table = None

    def visitNumberExpr(self, node):
        assert node.type == Type('Number')

    def visitStringExpr(self, node):
        assert node.type == Type('String')

    def visitFuncCallExpr(self, node):
        func_name = node.func_name
        if func_name not in self._cur_table:
            error("Unknown function %s" % func_name, node)
        elif not isinstance(self._cur_table[func_name], FuncDefinition):
            error("%s is not a function, it's a %s" % (func_name, self._cur_table[func_name]), node)

        symfunc = self._cur_table.find(func_name)[func_name]

        if node.type.known():
            symfunc.type.change(node.type.name)
        node.type = symfunc.type

        if len(node.args) != len(symfunc.args) and func_name != 'printf':
            error('Invalid number of arguments when calling function %s' % func_name, node)

        self._visit_list(node.args)

        for a, b in zip(symfunc.args, node.args):
            if b.type.known():
                a.type.change(b.type.name)
            b.type = a.type

        if not symfunc.type.known():
            symfunc.type.change(node.type.name)
        node.type = symfunc.type

    def visitExprStatement(self, node):
        self.visit(node.expr)

    def visitBlockStatement(self, node):
        self._visit_list(node.block)

    def visitTopLevel(self, node):
        with NewLexicalScope(self, node):
            self._visit_list(node.block)

    def visitFuncDefinition(self, node):
        if node.func_name in self._cur_table:
            error("Function %s already defined" % node.func_name, node)

        self._cur_table.add(node.func_name, node)
        with NewLexicalScope(self, node):
            self._current_function = node
            for arg in node.args:
                self._cur_table.add(arg.id, arg)
            self.visit(node.block)
            self._current_function = None
        
        # If we had no `return` statements, it's Void.
        if not node.type.known():
            node.type.change('Void')

    def visitIfStatement(self, node):
        self.visit(node.cond)

        with NewLexicalScope(self, node):
            self.visit(node.true_block)
            if node.false_block:
                self.visit(node.false_block)

    def visitBinaryOpExpr(self, node):
        self.visit(node.lhs)
        self.visit(node.rhs)

        if not node.lhs.type.known():
            node.lhs.type.change(node.rhs.type.name)
        elif not node.rhs.type.known():
            node.rhs.type.change(node.lhs.type.name)
        elif node.lhs.type != node.rhs.type:
            error("Types %s and %s is not the same." % (node.lhs.type, node.rhs.type), node)
        
        assert node.type == Type('dunno')
        node.type = node.lhs.type = node.rhs.type

    def visitIdExpr(self, node):
        if node.id not in self._cur_table:
            error("Unknown variable %s" % node.id, node)
        elif not isinstance(self._cur_table[node.id], IdExpr):
            error("%s is not a variable, it's a %s" % (node.id, self._cur_table[node.id]), node)

        symtable = self._cur_table.find(node.id)
        symnode = symtable[node.id]

        if symnode.type.incompatible(node.type):
            error("Non-matching types: %s and %s" % (node, symnode), node)

        if node.type.known():
            symnode.type.change(node.type.name)
        node.type = symnode.type

        node.var_idx = symtable.var_idx[node.id]

    def visitReturnStatement(self, node):
        self.visit(node.expr)
        assert node.expr.type is not None

        curfunc = self._current_function
        if not curfunc.type.known():
            curfunc.type.change(node.expr.type.name)
            node.expr.type = curfunc.type
        elif curfunc.type != node.expr.type:
            error("Returning %s but expecting %s" % (node.expr.type, curfunc.type), node)
