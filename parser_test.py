from equation_parser import Parser
from lexer import TokenType


def test_parser():
    p = Parser("a + b = c")
    result = p.parse()

    # should be parsed as
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

    # should be parsed as
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


def test_parser_parent_assignment():
    p = Parser("(a + b) * c")
    r = p.parse()

    # should be parsed as
    #     *
    #    / \
    #   +   c
    #  / \
    # a   b
    # Every node expect the * should have the parent assigned
    assert r.parent == None
    assert r.left.parent == r
    assert r.right.parent == r
    assert r.left.left.parent == r.left
    assert r.left.right.parent == r.left
