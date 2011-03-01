class BaseVisitor(object):
    def __init__(self, compiler):
        self._compiler = compiler

    def _visit_list(self, nodes):
        for node in nodes:
            node.accept(self)

    def visit(self, node):
        node.accept(self)
