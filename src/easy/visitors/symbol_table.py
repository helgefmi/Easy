import sys

from easy.visitors.base import BaseVisitor

class SymType(object):
    pass

class FunctionSymType(SymType):
    pass

class VariableSymType(SymType):
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
                'puts': FunctionSymType(),
                'printf': FunctionSymType(),
                'atoi': FunctionSymType(),
                'fflush': FunctionSymType(),
                'getchar': FunctionSymType(),
                'strlen': FunctionSymType(),
                'time': FunctionSymType(),
                'strcmp': FunctionSymType(),
                'strstr': FunctionSymType(),
                'strdup': FunctionSymType(),
            }
        self.parent = parent

    def add(self, symbol, type):
        if symbol in self:
            print "Unknown symbol '%s'"
            print str(self)
            exit(1)
        self[symbol] = type

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

class SymbolTableVisitor(BaseVisitor):
    def __init__(self, *args, **kwargs):
        super(SymbolTableVisitor, self).__init__(*args, **kwargs)
        self._cur_table = None

    def visitNumberExpr(self, node):
        pass

    def visitStringExpr(self, node):
        pass

    def visitFuncCallExpr(self, node):
        func_name = node.func_name
        if func_name not in self._cur_table:
            print "Unknown function name %s" % node.func_name
            print str(self._cur_table)
            exit(1)
        elif not isinstance(self._cur_table[func_name], FunctionSymType):
            print "%s is a %s, not a function" % (func_name,
                                                  self._cur_table[func_name])
            exit(1)
        self._visit_list(node.args)

    def visitExprStatement(self, node):
        self.visit(node.expr)

    def visitBlockStatement(self, node):
        self._visit_list(node.block)

    def visitTopLevel(self, node):
        with NewLexicalScope(self, node):
            self._visit_list(node.block)

    def visitFuncDefinition(self, node):
        self._cur_table.add(node.func_name, FunctionSymType())
        with NewLexicalScope(self, node):
            for arg in node.args:
                node.symtable.add(arg, VariableSymType())
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
        elif not isinstance(self._cur_table[node.id], VariableSymType):
            print "%s is not a variable, it's a %s" % (node.id,
                                                       self._cur_table[node.id])
            exit(1)
