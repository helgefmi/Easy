import sys

from easy.visitors.base import BaseVisitor

class IncIndent(object):
    def __init__(self, pprint):
        self._pprint = pprint

    def __enter__(self):
        self._pprint._indent += 1

    def __exit__(self, *args):
        self._pprint._indent -= 1

class PPrintVisitor(BaseVisitor):
    def __init__(self, *args, **kwargs):
        super(PPrintVisitor, self).__init__(*args, **kwargs)
        self._indent = 0

    def _print_indent(self):
        sys.stdout.write(' ' * (self._indent * 4))

    def visitNumberExpr(self, node):
        self._print_indent()
        print 'Number: %d' % node.number

    def visitStringExpr(self, node):
        self._print_indent()
        print 'String: "%s"' % node.string

    def visitFuncCallExpr(self, node):
        self._print_indent()
        print "FuncCall: %s, %d argument%s" % (node.func_name,
                                                len(node.args),
                                                '' if len(node.args) == 1 else 's')

        with IncIndent(self):
            self._visit_list(node.args)

    def visitExprStatement(self, node):
        self.visit(node.expr)

    def visitBlockStatement(self, node):
        self._print_indent()
        print "Block: %d element%s" % (len(node.block), \
                                       '' if len(node.block) == 1 else 's')

        with IncIndent(self):
            self._visit_list(node.block)

    def visitTopLevel(self, node):
        self._visit_list(node.block)

    def visitFuncDefinition(self, node):
        self._print_indent()
        print "FuncDefinition: %s, [%s]" % (node.func_name,
                                            ' '.join(map(str, node.args)))

        with IncIndent(self):
            self.visit(node.block)

    def visitIfStatement(self, node):
        self._print_indent()
        print "IfStatement: cond"
        with IncIndent(self):
            self.visit(node.cond)

        self._print_indent()
        print "IfStatement: true_block"
        with IncIndent(self):
            self.visit(node.true_block)

        if node.false_block:
            self._print_indent()
            print "IfStatement: false_block"
            with IncIndent(self):
                self.visit(node.false_block)

    def visitBinaryOpExpr(self, node):
        self._print_indent()
        print "BinaryOpExpr: %s" % node.operator
        with IncIndent(self):
            self.visit(node.lhs)
            self.visit(node.rhs)
    
    def visitIdExpr(self, node):
        self._print_indent()
        print "Identifier: %s" % node.id
