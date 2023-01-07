from typing import Set
from equation_parser import AST, BinOp, Num, UnaryOp, BinOp, Num, UnaryOp
from lexer import Token, TokenType
from utils import create_sym, inorder


class AnyOp(AST):
    """A wildcard node representing any node class with any token.
    Using AnyOp node indicates that the given query only checks existance of
    the node, and terminates further search on given branch from the point of encountering the AnyOp node.
    This is due to the fact that AnyOp could represent Num node, which does not have any children"""
    def __init__(self):
        self.token = Token("ANY", MatcherWildcardTokenType)
        pass


class MatcherWildcardTokenType():
    pass


class PatternMatcherException(Exception):
    pass

# TODO: wildcard unary and binary


def create_wildcard_num(parent: AST | None = None) -> Num:
    return Num(Token("ANY", MatcherWildcardTokenType), parent)


def create_wildcard_binop(parent: AST | None = None) -> BinOp:
    return BinOp(None, Token("ANY", MatcherWildcardTokenType), None, parent)


def create_wildcard_unary(parent: AST | None = None) -> UnaryOp:
    return UnaryOp(None, Token("ANY", MatcherWildcardTokenType), parent)


def create_compound_binop(compound_token_type: Set[TokenType], left: AST | None = None, right: AST | None = None, parent: AST | None = None) -> BinOp:
    """Creates compound-token-type binop node, used to match multiple selected token types with match() function"""
    return BinOp(left, Token("COMP", compound_token_type), right, parent=parent)


def create_compound_unary(compound_token_type: Set[TokenType], expr: AST | None = None, parent: AST | None = None) -> UnaryOp:
    """Creates compound-token-type unary node, used to match multiple selected token types with match() function"""
    return UnaryOp(expr, Token("COMP", compound_token_type), parent=parent)


def match(start: AST | None, pattern: AST | None) -> bool:
    """Returns true if the pattern is matched against the start tree
    Note: this will only match types of the tokens not the values!
    Note: this will match trees exactly, meaning that if the pattern
    exists somewhere in the start tree, but not on the beginning, then
    the function will output False, to check entire tree against the pattern
    apply this function over all tree nodes"""
    result = True

    if start != None and isinstance(pattern, AnyOp):
        pass #If current pattern node is a wildcard, check for start existance
    elif isinstance(start, BinOp) and isinstance(pattern, BinOp):
        # match subtrees
        if pattern.left != None:  # if none -> dont care about left subtree
            result &= match(start.left, pattern.left)
        if pattern.right != None:  # if none -> dont care about right subtree
            result &= match(start.right, pattern.right)
    elif isinstance(start, UnaryOp) and isinstance(pattern, UnaryOp):
        # match subtree
        if pattern.expr != None:
            result &= match(start.expr, pattern.expr)
    elif isinstance(start, Num) and isinstance(pattern, Num):
        pass 
    else:
        return False

    if pattern.token.type == MatcherWildcardTokenType:
        return result  # We dont care about type of the start node
    elif isinstance(pattern.token.type, set):
        result &= start.token.type in pattern.token.type
    elif isinstance(pattern.token.type, TokenType):
        result &= start.token.type == pattern.token.type
    else:
        raise PatternMatcherException(
            f"Invalid pattern token type {type(pattern.token.type)}")

    # base case
    return result
