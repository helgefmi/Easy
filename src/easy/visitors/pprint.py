import sys

from easy.visitors.base import BaseVisitor

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

        self._indent += 1
        self._visit_list(node.args)
        self._indent -= 1

    def visitExprStatement(self, node):
        self.visit(node.expr)

    def visitBlockStatement(self, node):
        self._print_indent()
        print "Block: %d element%s" % (len(node.block), \
                                       '' if len(node.block) == 1 else 's')

        self._indent += 1
        self._visit_list(node.block)
        self._indent -= 1

    def visitTopLevel(self, node):
        self._visit_list(node.block)

    def visitFuncDefinition(self, node):
        self._print_indent()
        print "FuncDefinition: %s, [%s]" % (node.func_name,
                                            ' '.join(map(str, node.args)))

        self._indent += 1
        self.visit(node.block)
        self._indent -= 1

    def visitIfStatement(self, node):
        self._print_indent()
        print "IfStatement: cond"
        self._indent += 1
        self.visit(node.cond)
        self._indent -= 1

        self._print_indent()
        print "IfStatement: true_block"
        self._indent += 1
        self.visit(node.true_block)
        self._indent -= 1

        if node.false_block:
            self._print_indent()
            print "IfStatement: false_block"
            self._indent += 1
            self.visit(node.false_block)
            self._indent -= 1
