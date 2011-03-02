import re

class Token(object):
    def __init__(self, token_type, token_value=None):
        self.type = token_type
        self.value = token_value

    def __str__(self):
        if self.type == 'tok_string':
            return '"%s"' % self.value
        if self.value is None:
            return self.type
        else:
            return str(self.value)

class Lexer(object):
    KEYWORDS = (
        'def', 'do', 'end',
        'if', 'then', 'else',
    )
    SYMBOLS = (
        ('(', 'tok_paren_start'),
        (')', 'tok_paren_end'),
        (';', 'tok_semicolon'),
        #('<', 'tok_lt'),
        #('>', 'tok_gt'),
        #('=', 'tok_assign'),
        #('*', 'tok_mul'),
        #('-', 'tok_sub'),
        #('/', 'tok_div'),
        #('+', 'tok_add'),
    )

    def __init__(self, input, filename=None):
        self.input = input
        self.tokens = []

    def lex(self):
        while True:
            self.input = self.input.lstrip()
            if self.input == '':
                break
            result = self.lex_identifier() or self.lex_number() \
                      or self.lex_symbol() or self.lex_string()
            if not result:
                return False
        return True

    def lex_string(self):
        if self.input[0] == '"':
            i = 1
            while i < len(self.input) and self.input[i] != '"':
                if self.input[i] == '\\' and self.input[i + 1] == '"':
                    i += 1
                i += 1
            string, self.input = self.input[1:i], self.input[i + 1:]
            self.tokens.append(Token('tok_string', string))
            return True
        return False

    def lex_identifier(self):
        match = re.match(r'[a-z][a-zA-Z0-9_]*', self.input)
        if match:
            id = match.group()
            self.input = self.input[len(id):]
            if id in self.KEYWORDS:
                token = Token('tok_%s' % id)
                self.tokens.append(token)
            else:
                self.tokens.append(Token('tok_identifier', id))
            return True
        return False

    def lex_symbol(self):
        for symbol, token in self.SYMBOLS:
            if self.input.startswith(symbol):
                self.input = self.input[len(symbol):]
                self.tokens.append(Token(token))
                return True
        return False

    def lex_number(self):
        i = 0
        while i < len(self.input) and self.input[i].isdigit():
            i += 1
        if i > 0:
            number, self.input = self.input[:i], self.input[i:]
            self.tokens.append(Token('tok_number', int(number)))
            return True
        return False
