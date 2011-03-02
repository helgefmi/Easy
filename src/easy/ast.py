# Abstract
class ASTNode(object):
    def accept(self, visitor):
        name = self.__class__.__name__
        getattr(visitor, 'visit%s' % name)(self)

class Expression(ASTNode):
    pass

class Statement(ASTNode):
    pass

# Expressions
class StringExpr(Expression):
    def __init__(self, string):
        self.string = string

    def __str__(self):
        return '"%s"' % self.string

class NumberExpr(Expression):
    def __init__(self, number):
        self.number = number

    def __str__(self):
        return '"%s"' % self.number

class FuncCallExpr(Expression):
    def __init__(self, func_name, args):
        self.func_name = func_name
        self.args = args

    def __str__(self):
        return '%s(%s)' % (self.func_name,
                           ' '.join(str(arg) for arg in self.args))

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
        ret = 'if %s then %s' % (str(self.cond), str(self.true_block))
        if self.false_block:
            ret += ' else %s' % self.false_block
        ret += ' end'
        return ret

# Other?
class FuncDefinition(ASTNode):
    def __init__(self, func_name, args, block):
        self.func_name = func_name
        self.args = args
        self.block = block

class TopLevel(ASTNode):
    def __init__(self, block):
        self.block = block

    def __str__(self):
        return str(self.block)
