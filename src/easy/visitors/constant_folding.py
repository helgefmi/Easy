from easy.ast import NumberExpr
from easy.visitors.base import BaseVisitor

class ConstantFoldingVisitor(BaseVisitor):
    def visitNumberExpr(self, node):
        return NumberExpr(node.number)

    def visitStringExpr(self, node):
        return NumberExpr(node.string)

    def visitFuncCallExpr(self, node):
        constants = self._visit_list(node.args)

        for i, constant in enumerate(constants):
            if constant is None:
                continue
            if node.args[i].is_leaf_node():
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
        if not (constant is None or constant.is_leaf_node()):
            node.cond = constant

        self.visit(node.true_block)
        if node.false_block:
            self.visit(node.false_block)

    def visitBinaryOpExpr(self, node):
        lconstant = self.visit(node.lhs)
        if not (lconstant is None or lconstant.is_leaf_node()):
            node.lhs = lconstant

        rconstant = self.visit(node.rhs)
        if not (rconstant is None or rconstant.is_leaf_node()):
            node.rhs = rconstant

        if lconstant is not None and rconstant is not None:
            if isinstance(lconstant, NumberExpr) and \
                isinstance(rconstant, NumberExpr):
                expr = '%s %s %s' % (lconstant.number,
                                     node.operator,
                                     rconstant.number)
                val = int(eval(expr))
                return NumberExpr(val)
