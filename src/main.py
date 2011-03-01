import sys
from easy.lexer import Lexer
from easy.parser import Parser
from easy.compiler import Compiler

if __name__ == "__main__":
    input = sys.stdin.read()

    lexer = Lexer(input)
    success = lexer.lex()
    if not success:
        print "lexer failed"
        print "input:", repr(lexer.input)
        print "tokens:", map(str, lexer.tokens)
        exit(1)
    print "lexer ok"

    parser = Parser(lexer.tokens)
    success = parser.parse()
    if not success:
        print "parser failed"
        print "tokens:", map(str, parser.tokens)
        print "ast:", parser.ast
        exit(1)
    print "parser ok"

    compiler = Compiler(parser.ast)
    success = compiler.compile()
    if not success:
        print "compiler failed"
        print "ast:", compiler.ast
        print "compileretlant", compiler
        exit(1)
    print "compiler ok"
    
    open('out.s', 'w').write(compiler.output)
