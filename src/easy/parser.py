from easy.ast import *

class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
    
    def _eat_token(self, what):
        token, self.tokens = self.tokens[0], self.tokens[1:]
        assert token.type == what
        return token

    def _eat_if_token(self, what):
        if self._curtype() == what:
            return self._eat_token(what)

    def _curtype(self):
        return self.tokens[0].type

    def parse(self):
        self.ast = TopLevel(self.parse_block())
        assert len(self.tokens) == 0
        return True

    def parse_block(self):
        block = []
        while self.tokens:
            expr = self.parse_expression()
            self._eat_token('tok_semicolon')
            assert expr
            expr = ExprStatement(expr)
            block.append(expr)
        return BlockStatement(block)

    def parse_expression(self):
        return self.parse_string() or self.parse_identifier()

    def parse_string(self):
        string = self._eat_if_token('tok_string')
        if not string:
            return False
        return StringExpr(string.value)

    def parse_identifier(self):
        id = self._eat_if_token('tok_identifier')
        if not id:
            return False

        if self._eat_if_token('tok_paren_start'):
            args = []
            while self._curtype() != 'tok_paren_end':
                args.append(self.parse_expression())
            self._eat_token('tok_paren_end')
            return FuncCallExpr(id, args)
