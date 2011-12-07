from easy.ast import NumberExpr
from easy.visitors.base import BaseVisitor

class ConstantFoldingVisitor(BaseVisitor):
    def visitNumberExpr(self, node):
        return node

    def visitStringExpr(self, node):
        return node

    def visitFuncCallExpr(self, node):
        constants = self._visit_list(node.args)

        for i, constant in enumerate(constants):
            if constant is None:
                continue
            node.args[i] = constant

    def visitExprStatement(self, node):
        return self.visit(node.expr)

    def visitBlockStatement(self, node):
        self._visit_list(node.block)

    def visitTopLevel(self, node):
        self._visit_list(node.block)

    def visitFuncDefinition(self, node):
        self.visit(node.block)

    def visitIfStatement(self, node):
        constant = self.visit(node.cond)
        if constant and not node.cond != constant:
            node.cond = constant

        self.visit(node.true_block)
        if node.false_block:
            self.visit(node.false_block)

    def visitBinaryOpExpr(self, node):
        lconstant = self.visit(node.lhs)
        if lconstant and node.lhs != lconstant:
            node.lhs = lconstant

        rconstant = self.visit(node.rhs)
        if rconstant and node.rhs != rconstant:
            node.rhs = rconstant

        if lconstant is None or rconstant is None:
            return

        if (isinstance(lconstant, NumberExpr) and isinstance(rconstant, NumberExpr)):
            expr = '%s %s %s' % (lconstant.number,
                                    node.operator,
                                    rconstant.number)
            val = int(eval(expr))
            return NumberExpr(val)

    def visitIdExpr(self, node):
        pass

    def visitReturnStatement(self, node):
        self.visit(node.expr)
