#!/usr/bin/env python
import sys

from easy.compiler import Compiler
from easy.lexer import Lexer
from easy.parser import Parser

if __name__ == "__main__":
    input = sys.stdin.read()

    lexer = Lexer(input)
    tokens = lexer.lex()
    if not tokens:
        print "lexer failed"
        exit(1)
    print "lexer ok"

    parser = Parser(tokens)
    ast = parser.parse()
    if not ast:
        print "parser failed"
        exit(1)
    print "parser ok"

    compiler = Compiler(ast)
    output = compiler.compile()
    if not output:
        print "compiler failed"
        exit(1)
    print "compiler ok"
    
    with open('out.s', 'w') as f:
        f.write(output)
