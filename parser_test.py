from parser import Parser
from lexer import TokenType

def test_parser():
    p = Parser("a + b = c")
    result = p.parse()

    #should be parsed as
    #     =
    #    / \
    #   +   c
    #  / \
    # a   b
    assert (result.op.type == TokenType.EQ 
    and result.left.op.type == TokenType.PLUS
    and result.left.left.token.type == TokenType.SYM
    and result.left.right.token.type == TokenType.SYM
    and result.right.token.type == TokenType.SYM)



def test_parser_parenthesis():
    p = Parser("(a + b) * c")
    result = p.parse()

    #should be parsed as
    #     *
    #    / \
    #   +   c
    #  / \
    # a   b
    assert (result.op.type == TokenType.MUL 
    and result.left.op.type == TokenType.PLUS
    and result.left.left.token.type == TokenType.SYM
    and result.left.right.token.type == TokenType.SYM
    and result.right.token.type == TokenType.SYM)