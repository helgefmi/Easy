from easy.visitors.codegen import CodeGenVisitor
from easy.visitors.constant_folding import ConstantFoldingVisitor
from easy.visitors.symbol_table import SymbolTableVisitor
from easy.visitors.pprint import PPrintVisitor

class Compiler(object):
    def __init__(self, ast):
        self._ast = ast

    def _do_pass(self, visitor):
        return visitor.visit(self._ast)

    def compile(self):
        self._do_pass(ConstantFoldingVisitor(self))
        self._do_pass(SymbolTableVisitor(self))
        self._do_pass(PPrintVisitor(self))

        codegen_visitor = CodeGenVisitor(self)
        output = self._do_pass(codegen_visitor)

        return output
