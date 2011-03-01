from easy.ast import *

class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
    
    def _eat_token(self, what):
        token, self.tokens = self.tokens[0], self.tokens[1:]
        assert token.type == what, "Expected %s, got %s." % (what, token.type)
        return token

    def _eat_if_token(self, what):
        if self._curtype() == what:
            return self._eat_token(what)

    def _curtype(self):
        return self.tokens[0].type

    def parse(self):
        toplevel = []
        while self.tokens:
            toplevel.append(self.parse_function())
        self.ast = TopLevel(toplevel)
        return True

    def parse_expression(self):
        return self.parse_string() or self.parse_identifier() \
                or self.parse_number()

    def parse_block(self):
        block = []
        self._eat_token('tok_do')
        while True:
            expr = self.parse_expression()
            self._eat_token('tok_semicolon')
            assert expr
            expr = ExprStatement(expr)
            block.append(expr)
            if self._eat_if_token('tok_end'):
                break
        return BlockStatement(block)

    def parse_function(self):
        token = self._eat_token('tok_def')
        if not token:
            return False
        
        func_name = self.parse_identifier(parse_funccall=False)

        args = []
        if self._eat_if_token('tok_paren_start'):
            while self._curtype() != 'tok_paren_end':
                args.append(self.parse_identifier(parse_funccall=False))
            self._eat_token('tok_paren_end')

        block = self.parse_block()

        return FuncDefinition(func_name, args, block)

    def parse_number(self):
        number = self._eat_if_token('tok_number')
        if not number:
            return False
        return NumberExpr(number.value)

    def parse_string(self):
        string = self._eat_if_token('tok_string')
        if not string:
            return False
        return StringExpr(string.value)

    def parse_identifier(self, parse_funccall=True):
        id = self._eat_if_token('tok_identifier')
        if not id:
            return False

        if not parse_funccall:
            return id

        if self._eat_if_token('tok_paren_start'):
            args = []
            while self._curtype() != 'tok_paren_end':
                args.append(self.parse_expression())
            self._eat_token('tok_paren_end')
            return FuncCallExpr(id, args)
