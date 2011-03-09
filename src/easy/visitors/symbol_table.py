import sys

from easy.visitors.base import BaseVisitor
from easy.types import Void, Number, String

class SymType(object):
    pass

class FunctionSymType(SymType):
    def __init__(self, type, arg_types):
        self.type = type
        self.arg_types = arg_types

class VariableSymType(SymType):
    def __init__(self, type):
        self.type = type

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
                'puts': FunctionSymType(Void, [String]),
                'printf': FunctionSymType(Void, []),
                'atoi': FunctionSymType(Number, [String]),
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

    def add(self, symbol, type):
        if symbol in self:
            print "Unknown symbol '%s'"
            print str(self)
            exit(1)
        self[symbol] = type

        if isinstance(type, VariableSymType):
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
        assert node.type is Number

    def visitStringExpr(self, node):
        assert node.type is String

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

        assert node.type is None
        node.type = self._cur_table[func_name].type
        assert node.type is not None

        self._visit_list(node.args)

        func_type = self._cur_table[func_name].type
        func_arg_types = self._cur_table[func_name].arg_types
        arg_types = [arg.type for arg in node.args]

        # TODO :-)
        if func_name == 'printf':
            return

        if len(func_arg_types) != len(arg_types):
            print "Called %s with invalid amount of arguments %s, expecting %s" % (
                func_name, map(str, arg_types), map(str, func_arg_types)
            )
            exit(1)
        for i, arg_type in enumerate(arg_types):
            if arg_type is not func_arg_types[i]:
                print "Called %s with invalid types %s, expecting %s" % (
                    func_name, map(str, arg_types), map(str, func_arg_types)
                )
                exit(1)

    def visitExprStatement(self, node):
        self.visit(node.expr)

    def visitBlockStatement(self, node):
        self._visit_list(node.block)

    def visitTopLevel(self, node):
        with NewLexicalScope(self, node):
            self._visit_list(node.block)

    def visitFuncDefinition(self, node):
        func_type = FunctionSymType(node.type, [arg.type for arg in node.args])
        self._cur_table.add(node.func_name, func_type)
        with NewLexicalScope(self, node):
            for arg in node.args:
                node.symtable.add(arg.id, VariableSymType(arg.type))
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
        if node.lhs.type is not node.rhs.type:
            print "hmz"
            print str(node.lhs.type), str(node.lhs)
            print str(node.rhs.type), str(node.rhs)
            exit(1)
        assert node.lhs.type is not None
        assert node.rhs.type is not None

        assert node.type is None
        node.type = node.lhs.type
    
    def visitIdExpr(self, node):
        if node.id not in self._cur_table:
            print "Unknown variable %s" % node.id
            exit(1)
        elif not isinstance(self._cur_table[node.id], VariableSymType):
            print "%s is not a variable, it's a %s" % (node.id,
                                                       self._cur_table[node.id])
            exit(1)

        node.var_idx = self._cur_table.find(node.id).var_idx[node.id]
        if node.type is None:
            node.type = self._cur_table[node.id].type

        if node.type is None:
            print "Unknown type of identifier %s" % node
            exit(1)

    def visitReturnStatement(self, node):
        self.visit(node.expr)
