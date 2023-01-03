from equation_parser import BinOp, Num
from lexer import Token
import utils


def test_distance():
    #    1
    #    /\
    #   /  \
    #  2    5
    # / \  / \
    # 3   4 6  7
    tree = BinOp(BinOp(Num(Token(3, None)), Token(2, None), Num(Token(4, None))), Token(
        1, None), BinOp(Num(Token(6, None)), Token(5, None), Num(Token(7, None))))

    assert 2 == utils.distance(tree.left.left, tree.left.right)
    assert 4 == utils.distance(tree.left.left, tree.right.right)
    assert 1 == utils.distance(tree, tree.right)


def test_inorder():
    #    1
    #    /\
    #   /  \
    #  2    5
    # / \  / \
    # 3   4 6  7
    tree = BinOp(BinOp(Num(Token(3, None)), Token(2, None), Num(Token(4, None))), Token(
        1, None), BinOp(Num(Token(6, None)), Token(5, None), Num(Token(7, None))))
    result = utils.inorder(tree)
    result = list(map(lambda x: x.token.value, result))
    assert [3, 2, 4, 1, 6, 5, 7] == result


def test_trace():
    # 2 + a = b * c
    #    =
    #    /\
    #   /  \
    #  +    *
    # / \  / \
    # 2   a b  c
    test_str = "(2+a)=(b*c)"
    tree = BinOp(BinOp(Num(Token(2, None)), Token("+", None), Num(Token("a", None))),
                 Token("=", None), BinOp(Num(Token("b", None)), Token("*", None), Num(Token("c", None))))
    assert test_str == utils.trace(tree)
