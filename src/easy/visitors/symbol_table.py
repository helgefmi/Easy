from easy.ast import FuncDefinition, IdExpr
from easy.visitors.base import BaseVisitor

class SymType(object):
    pass

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
                'puts': FuncDefinition('puts', [IdExpr('_a', 'String')], [], 'Void'),
                'atoi': FuncDefinition('atoi', [IdExpr('_a', 'String')], [], 'Void'),
                'printf': None,
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
            print "Unknown symbol '%s'"
            print str(self)
            exit(1)
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
        self._cur_function = None
        self._checks = []

    def visitNumberExpr(self, node):
        pass

    def visitStringExpr(self, node):
        pass

    def visitFuncCallExpr(self, node):
        func_name = node.func_name
        assert func_name in self._cur_table, func_name

        self._visit_list(node.args)

    def visitExprStatement(self, node):
        self.visit(node.expr)

    def visitBlockStatement(self, node):
        self._visit_list(node.block)

    def visitTopLevel(self, node):
        with NewLexicalScope(self, node):
            self._visit_list(node.block)

        for check in self._checks:
            check()

    def visitFuncDefinition(self, node):
        self._cur_function = node

        self._cur_table.add(node.func_name, node)
        with NewLexicalScope(self, node):
            for arg in node.args:
                node.symtable.add(arg.id, arg)
            self.visit(node.block)

    def visitIfStatement(self, node):
        self.visit(node.cond)

        with NewLexicalScope(self, node):
            self.visit(node.true_block)
            if node.false_block:
                self.visit(node.false_block)

    def visitBinaryOpExpr(self, node):
        self.visit(node.lhs)
        self.visit(node.rhs)

    def visitIdExpr(self, node):
        if node.id not in self._cur_table:
            print "Unknown variable %s" % node.id
            exit(1)
        elif not isinstance(self._cur_table[node.id], IdExpr):
            print "%s is not a variable, it's a %s" % (node.id,
                                                       self._cur_table[node.id])
            exit(1)

        node.var_idx = self._cur_table.find(node.id).var_idx[node.id]

    def visitReturnStatement(self, node):
        self.visit(node.expr)
