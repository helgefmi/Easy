import re

class Token(object):
    def __init__(self, lineno, token_type, token_value=None):
        self._type = token_type
        self._value = token_value
        self._lineno = lineno

    @property
    def type(self):
        return self._type

    @property
    def value(self):
        return self._value

    @property
    def lineno(self):
        return self._lineno

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
        'return',
    )
    SYMBOLS = (
        ('>=', 'tok_binary_op'),
        ('<=', 'tok_binary_op'),
        ('==', 'tok_binary_op'),
        ('!=', 'tok_binary_op'),
        ('<',  'tok_binary_op'),
        ('>',  'tok_binary_op'),
        ('*',  'tok_binary_op'),
        ('-',  'tok_binary_op'),
        ('/',  'tok_binary_op'),
        ('+',  'tok_binary_op'),
        ('(',  'tok_paren_start'),
        (')',  'tok_paren_end'),
        (';',  'tok_semicolon'),
    )

    def __init__(self, input, filename=None):
        self.input = input
        self._tokens = []
        self._lineno = 1

    def _append(self, type, value=None):
        token = Token(self._lineno, type, value)
        self._tokens.append(token)

    def _strip_whitespace(self):
        for i, char in enumerate(self.input):
            if not char.isspace():
                break
            if char == '\n':
                self._lineno += 1
        self.input = self.input.lstrip()

    def _assert(self, cond, error, lineno=None):
        lineno = lineno or self._lineno
        if not cond:
            print error
            print 'At line %d' % lineno
            print 'input[:10] = %s' % repr(self.input[:10])
            exit(1)

    def lex(self):
        while True:
            self._strip_whitespace()
            if not self.input:
                break
            result = self.lex_identifier() or self.lex_number() \
                      or self.lex_symbol() or self.lex_string()
            self._assert(result, 'Unexpected input')
        return self._tokens

    def lex_string(self):
        if self.input[0] != '"':
            return False

        self.input = self.input[1:]

        start_lineno = self._lineno
        last = None
        for i, char in enumerate(self.input):
            if char == '\n':
                self._lineno += 1
            if char == '"' and last != '\\':
                break
            last = char
        else:
            self._assert(False, 'Unterminated string literal; expecting "',
                         start_lineno)

        string, self.input = self.input[:i], self.input[i + 1:]
        self._append('tok_string', string)
        return True

    def lex_identifier(self):
        match = re.match(r'[a-z][a-zA-Z0-9_]*', self.input)
        if not match:
            return False

        id = match.group()
        self.input = self.input[match.end():]
        if id in self.KEYWORDS:
            self._append('tok_%s' % id)
        else:
            self._append('tok_identifier', id)
        return True

    def lex_symbol(self):
        for symbol, token in self.SYMBOLS:
            if self.input.startswith(symbol):
                self.input = self.input[len(symbol):]
                self._append(token, symbol)
                return True
        return False

    def lex_number(self):
        for i, char in enumerate(self.input):
            if not char.isdigit():
                break

        if i == 0:
            return False

        number, self.input = self.input[:i], self.input[i:]
        self._append('tok_number', int(number))
        return True
