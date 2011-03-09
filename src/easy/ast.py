from easy.types import get_or_create_type

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
        self.type = get_or_create_type('String')

    def __str__(self):
        return '"%s"' % self.string

class NumberExpr(Expression):
    def __init__(self, number):
        self.number = number
        self.type = get_or_create_type('Number')

    def __str__(self):
        return '"%s"' % self.number

class BinaryOpExpr(Expression):
    def __init__(self, operator, lhs, rhs):
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs
        self.type = None

    def __str__(self):
        return '"%s %s %s"' % (self.lhs, self.operator, self.rhs)

class FuncCallExpr(Expression):
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args
        self.type = None

    def __str__(self):
        return '%s(%s)' % (self.func_name,
                           ' '.join(str(arg) for arg in self.args))

class IdExpr(Expression):
    def __init__(self, id, type_name):
        self.id = id
        self.type = get_or_create_type(type_name) or None

    def __str__(self):
        return '%s %s' % (self.type, self.id)

# Statements
class BlockStatement(Statement):
    def __init__(self, block):
        self.block = block

    def __str__(self):
        return '; '.join(map(str, self.block)) + ';'

class ExprStatement(Statement):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return str(self.expr)

class IfStatement(Statement):
    def __init__(self, cond, true_block, false_block):
        self.cond = cond
        self.true_block = true_block
        self.false_block = false_block

    def __str__(self):
        ret = 'if %s then %s' % (self.cond, self.true_block)
        if self.false_block:
            ret += ' else %s' % self.false_block
        ret += ' end'
        return ret

class ReturnStatement(Statement):
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return 'return %s' % self.expr

# Other?
class FuncDefinition(ASTNode):
    def __init__(self, func_name, args, block, type_name):
        self.func_name = func_name
        self.args = args
        self.block = block
        self.type = get_or_create_type(type_name) or None

class TopLevel(ASTNode):
    def __init__(self, block):
        self.block = block

    def __str__(self):
        return str(self.block)
