class BaseVisitor(object):
    def __init__(self, compiler):
        self._compiler = compiler

    def _visit_list(self, nodes, *args, **kwargs):
        return [self.visit(node) for node in nodes]

    def visit(self, node, *args, **kwargs):
        return node.accept(self, *args, **kwargs)
