from easy.ast import *

class Parser(object):
    def __init__(self, tokens):
        self.tokens = tokens
    
    def _next_tokens(self, *args):
        if len(args) > len(self.tokens):
            return False
        for i, arg in enumerate(args):
            if self.tokens[i].type != arg:
                return False
        return True

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
            function = self.parse_function()
            assert function, map(str, self.tokens)[:10]
            toplevel.append(function)
        self.ast = TopLevel(toplevel)
        return True

    def parse_expression(self):
        return self.parse_string() or self.parse_number() or self.parse_funccall()

    def parse_statement(self):
        return self.parse_if() or ExprStatement(self.parse_expression())

    def parse_number(self):
        token = self._eat_if_token('tok_number')
        return NumberExpr(token.value) if token else False

    def parse_string(self):
        token = self._eat_if_token('tok_string')
        return StringExpr(token.value) if token else False

    def parse_if(self):
        if not self._eat_if_token('tok_if'):
            return False

        cond = self.parse_expression()
        self._eat_if_token('tok_then')
        true_block = self.parse_block(end_tokens=['tok_else', 'tok_end'])
        false_block = None

        if self._eat_if_token('tok_else'):
            false_block = self.parse_block(end_tokens='tok_end')
        self._eat_token('tok_end')

        return IfStatement(cond, true_block, false_block)

    def parse_function(self):
        if not self._eat_if_token('tok_def'):
            return False
        
        func_name = self._eat_token('tok_identifier').value

        args = []
        if self._eat_if_token('tok_paren_start'):
            while self._curtype() == 'tok_identifier':
                arg = self._eat_token('tok_identifier').value
                assert arg, map(str, self.tokens)[:10]
                args.append(arg)
            self._eat_token('tok_paren_end')

        self._eat_token('tok_do')
        block = self.parse_block(end_tokens='tok_end')
        self._eat_token('tok_end')
        return FuncDefinition(func_name, args, block)

    def parse_block(self, end_tokens):
        if isinstance(end_tokens, str):
            end_tokens = (end_tokens,)

        block = []
        while True:
            expr = self.parse_statement() or self.parse_expression()
            assert expr, map(str, self.tokens)[:10]
            self._eat_if_token('tok_semicolon')
            block.append(expr)
            if self._curtype() in end_tokens:
                break
        return BlockStatement(block)

    def parse_funccall(self):
        if not self._next_tokens('tok_identifier', 'tok_paren_start'):
            return False

        func_name = self._eat_token('tok_identifier')
        self._eat_token('tok_paren_start')
        args = []
        while self._curtype() != 'tok_paren_end':
            expr = self.parse_expression()
            assert expr, map(str, self.tokens)[:10]
            args.append(expr)
        self._eat_token('tok_paren_end')
        return FuncCallExpr(func_name, args)
