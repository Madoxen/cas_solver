from lexer import TokenType
from pattern_matcher import AnyOp, create_compound_binop, match
from equation_parser import Parser


def test_basic_match():
    tree = Parser("x=1").parse()
    pattern = Parser("x=1").parse()
    assert True == match(tree, pattern)


def test_compound_match():
    tree = Parser("x+1").parse()
    pattern = create_compound_binop(
        {TokenType.PLUS, TokenType.MINUS}, left=AnyOp(), right=AnyOp())
    assert True == match(tree, pattern)
    tree = Parser("x-1").parse()
    assert True == match(tree, pattern)


def test_non_trivial_match():
    pattern = create_compound_binop({TokenType.PLUS, TokenType.MINUS},
                                    left=create_compound_binop(
                                        {TokenType.PLUS, TokenType.MINUS}, left=AnyOp(), right=AnyOp()),
                                    right=AnyOp())
    #Matches: U +- V +- Z
    tree = Parser("(x+1)+1-x").parse()
    assert True == match(tree, pattern)
