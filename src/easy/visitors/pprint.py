import sys

from easy.visitors.base import BaseVisitor

class PPrintVisitor(BaseVisitor):
    def __init__(self, *args, **kwargs):
        super(PPrintVisitor, self).__init__(*args, **kwargs)
        self._indent = 0

    def _print_indent(self):
        sys.stdout.write(' ' * (self._indent * 4))

    def visitStringExpr(self, node):
        self._print_indent()
        print 'String: "%s"' % node.string

    def visitFuncCallExpr(self, node):
        self._print_indent()
        print "FuncCall: %s, %d argument%s" % (node.func_name,
                                                len(node.args),
                                                '' if len(node.args) == 1 else 's')

        self._indent += 1
        self._visit_list(node.args)
        self._indent -= 1

    def visitExprStatement(self, node):
        self.visit(node.expr)

    def visitBlockStatement(self, node):
        self._print_indent()
        print "Block: %d elements" % len(node.block)

        self._indent += 1
        self._visit_list(node.block)
        self._indent -= 1
