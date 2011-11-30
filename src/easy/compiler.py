from easy.visitors.codegen import CodeGenVisitor
from easy.visitors.constant_folding import ConstantFoldingVisitor
from easy.visitors.pprint import PPrintVisitor
from easy.visitors.symbol_table import SymbolTableVisitor

class Compiler(object):
    def __init__(self, ast):
        self._ast = ast

    def _do_pass(self, visitor):
        return visitor.visit(self._ast)

    def compile(self):
        self._do_pass(SymbolTableVisitor(self))
        self._do_pass(ConstantFoldingVisitor(self))
        self._do_pass(PPrintVisitor(self))

        output = self._do_pass(CodeGenVisitor(self))

        return output
