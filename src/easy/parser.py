from easy import ast

class Parser(object):
    def __init__(self, tokens):
        self._tokens = tokens
    
    def _get_current_lineno(self):
        return self._tokens[0].lineno if self._tokens else -1

    def _assert(self, cond, expected):
        if not cond:
            lineno = self._get_current_lineno()
            if cond is not False:
                expected += ", got %s" % cond
            print expected
            print "Probably line %d" % lineno
            print "tokens[:10] = %s" % map(str, self._tokens)[:10]
            exit(1)

    def _next_tokens(self, *args):
        if len(args) > len(self._tokens):
            return False
        for i, arg in enumerate(args):
            if self._tokens[i].type != arg:
                return False
        return True

    def _eat_token(self, what):
        token, self._tokens = self._tokens[0], self._tokens[1:]
        self._assert(token.type == what, "Expected %s, got %s." % (what, token.type))
        return token

    def _eat_if_token(self, what):
        if self._curtype() == what:
            return self._eat_token(what)

    def _curtype(self):
        return self._tokens[0].type if self._tokens else None

    def parse(self):
        toplevel = []
        while self._tokens:
            function = self.parse_function()
            self._assert(function, "Expected function")
            toplevel.append(function)
        return ast.TopLevel(toplevel)

    def parse_expression(self):
        lineno_before = self._get_current_lineno()
        expr = (self.parse_string() or self.parse_number() or
               self.parse_funccall() or self.parse_identifier() or
               self.parse_paren_expression())

        if self._curtype() == 'tok_binary_op':
            token = self._eat_token('tok_binary_op')
            rhs = self.parse_expression()
            expr = ast.BinaryOpExpr(token.value, expr, rhs)
        lineno_after = self._get_current_lineno()

        expr.lineno_between = (lineno_before, lineno_after)
        return expr

    def parse_statement(self):
        lineno_before = self._get_current_lineno()
        statement = self.parse_if() or self.parse_return()
        if not statement:
            expr = self.parse_expression()
            if not expr:
                return None
            statement = ast.ExprStatement(expr)
        lineno_after = self._get_current_lineno()

        statement.lineno_between = (lineno_before, lineno_after)
        return statement

    def parse_paren_expression(self):
        if not self._eat_if_token('tok_paren_start'):
            return False
        expr = self.parse_expression()
        self._eat_token('tok_paren_end')
        return expr

    def parse_number(self):
        token = self._eat_if_token('tok_number')
        return ast.NumberExpr(token.value) if token else False

    def parse_string(self):
        token = self._eat_if_token('tok_string')
        return ast.StringExpr(token.value) if token else False

    def parse_identifier(self):
        type = None
        if self._next_tokens('tok_type', 'tok_identifier'):
            type = self._eat_token('tok_type').value

        token = self._eat_if_token('tok_identifier')
        return ast.IdExpr(token.value, type) if token else False

    def parse_funccall(self):
        if not self._next_tokens('tok_identifier', 'tok_paren_start'):
            return False

        func_name = self._eat_token('tok_identifier').value
        self._eat_token('tok_paren_start')

        args = []
        while self._curtype() != 'tok_paren_end':
            expr = self.parse_expression()
            self._assert(expr, 'Expected expression')
            args.append(expr)

        self._eat_token('tok_paren_end')
        return ast.FuncCallExpr(func_name, args)

    def parse_if(self):
        if not self._eat_if_token('tok_if'):
            return False

        cond = self.parse_expression()
        self._eat_token('tok_then')
        true_block = self.parse_block(end_tokens=['tok_else', 'tok_end'])
        false_block = None

        if self._eat_if_token('tok_else'):
            false_block = self.parse_block(end_tokens='tok_end')
        self._eat_token('tok_end')

        return ast.IfStatement(cond, true_block, false_block)

    def parse_function(self):
        if not self._eat_if_token('tok_def'):
            return False
        
        type = self._eat_if_token('tok_type')
        func_name = self._eat_token('tok_identifier').value

        args = []
        if self._eat_if_token('tok_paren_start'):
            while self._curtype() != 'tok_paren_end':
                id = self.parse_identifier()
                args.append(id)
            self._eat_token('tok_paren_end')

        self._eat_token('tok_do')
        block = self.parse_block(end_tokens='tok_end')
        self._eat_token('tok_end')

        return ast.FuncDefinition(func_name, args, block, type.value if type else None)

    def parse_block(self, end_tokens):
        if isinstance(end_tokens, str):
            end_tokens = (end_tokens,)

        block = []
        while self._curtype() not in end_tokens:
            expr = self.parse_statement() or self.parse_expression()
            self._assert(expr, 'Expected statement')
            self._eat_if_token('tok_semicolon')
            block.append(expr)
        return ast.BlockStatement(block)

    def parse_return(self):
        if not self._eat_if_token('tok_return'):
            return False

        expr = self.parse_expression()
        self._assert(expr, 'Expected expression')
        return ast.ReturnStatement(expr)
