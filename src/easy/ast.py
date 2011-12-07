from easy.type import Type

# Abstract
class ASTNode(object):
    def accept(self, visitor, *args, **kwargs):
        name = self.__class__.__name__
        return getattr(visitor, 'visit%s' % name)(self, *args, **kwargs)

    def is_leaf_node(self):
        return isinstance(self, StringExpr) or isinstance(self, NumberExpr)

class Expression(ASTNode):
    pass

class Statement(ASTNode):
    pass

# Expressions
class StringExpr(Expression):
    def __init__(self, string):
        self.string = string
        self.type = Type('String')

class NumberExpr(Expression):
    def __init__(self, number):
        self.number = number
        self.type = Type('Number')

class BinaryOpExpr(Expression):
    def __init__(self, operator, lhs, rhs):
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs
        self.type = Type('dunno')

class FuncCallExpr(Expression):
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args
        self.type = Type('dunno')

class IdExpr(Expression):
    def __init__(self, id, type):
        self.id = id
        self.type = Type(type) if type else Type('dunno')

# Statements
class BlockStatement(Statement):
    def __init__(self, block):
        self.block = block

class ExprStatement(Statement):
    def __init__(self, expr):
        self.expr = expr

class IfStatement(Statement):
    def __init__(self, cond, true_block, false_block):
        self.cond = cond
        self.true_block = true_block
        self.false_block = false_block

class ReturnStatement(Statement):
    def __init__(self, expr):
        self.expr = expr

# Other?
class FuncDefinition(ASTNode):
    def __init__(self, func_name, args, block, type):
        self.func_name = func_name
        self.args = args
        self.block = block
        self.type = Type(type) if type else Type('dunno')

class TopLevel(ASTNode):
    def __init__(self, block):
        self.block = block
