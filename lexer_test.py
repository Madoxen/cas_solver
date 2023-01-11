from lexer import Lexer, TokenType


def test_lexer_simple_num():
    l = Lexer()
    r = l.lex("1")
    assert r[0].type == TokenType.NUM and r[0].value == 1
    l = Lexer()
    r = l.lex("12")
    assert r[0].type == TokenType.NUM and r[0].value == 12


def test_lexer_simple_sym():
    l = Lexer()
    r = l.lex("a")
    assert r[0].type == TokenType.SYM and r[0].value == "a"
    l = Lexer()
    r = l.lex("ab")
    assert r[0].type == TokenType.SYM and r[0].value == "ab"


def test_lexer_expression():
    input = "a + b"
    l = Lexer()
    r = l.lex(input)
    assert (r[0].type == TokenType.SYM
            and r[1].type == TokenType.PLUS
            and r[2].type == TokenType.SYM
            and r[3].type == TokenType.EOF)


def test_lexer_expression_parenthesis():
    input = "(a + b)"
    l = Lexer()
    r = l.lex(input)
    assert (r[0].type == TokenType.LPAREN
            and r[1].type == TokenType.SYM
            and r[2].type == TokenType.PLUS
            and r[3].type == TokenType.SYM
            and r[4].type == TokenType.RPAREN
            and r[5].type == TokenType.EOF)


def test_lexer_expression_whitespace_skips():
    input = "   (  a  +   b)   "
    l = Lexer()
    r = l.lex(input)
    assert (r[0].type == TokenType.LPAREN
            and r[1].type == TokenType.SYM
            and r[2].type == TokenType.PLUS
            and r[3].type == TokenType.SYM
            and r[4].type == TokenType.RPAREN
            and r[5].type == TokenType.EOF)
