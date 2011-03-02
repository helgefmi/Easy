from easy.visitors.pprint import PPrintVisitor
from easy.visitors.codegen import CodeGenVisitor

class Compiler(object):
    def __init__(self, ast):
        self._ast = ast

    def _do_pass(self, visitor):
        return visitor.visit(self._ast)

    def compile(self):
        self._do_pass(PPrintVisitor(self))

        codegen_visitor = CodeGenVisitor(self)
        output = self._do_pass(codegen_visitor)

        return output
