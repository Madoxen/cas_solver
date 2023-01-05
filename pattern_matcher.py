from equation_parser import AST, BinOp, Num, UnaryOp
from lexer import Token, TokenType
from utils import create_sym, inorder

class MatcherWildcard():
    pass

#TODO: wildcard unary and binary 
def create_wild_card_num(parent: AST = None) -> Num:
    return Num(Token("ANY", MatcherWildcard), parent)

def create_wild_card_binop(parent: AST = None) -> Num:
    return BinOp(None,Token("ANY", MatcherWildcard), None, parent)

def create_wild_card_unary(parent: AST = None) -> Num:
    return UnaryOp(None,Token("ANY", MatcherWildcard), parent)


def match(start: AST, pattern: AST) -> bool:
    """Returns true if the pattern is matched against the start tree
    Note: this will only match types of the tokens not the values!
    Note: this will match trees exactly, meaning that if the pattern
    exists somewhere in the start tree, but not on the beginning, then
    the function will output False, to check entire tree against the pattern
    apply this function over all tree nodes"""
    if type(start) != type(pattern):
        return False

    result = True
    if isinstance(start, BinOp) and isinstance(pattern, BinOp):
        #match subtrees 
        if pattern.left != None: #if none -> dont care about left subtree
            result &= match(start.left, pattern.left)
        if pattern.right != None: #if none -> dont care about right subtree
            result &= match(start.right, pattern.right)
    elif isinstance(start, UnaryOp) and isinstance(pattern, UnaryOp): 
        #match subtree
        if pattern.expr != None:
            result &= match(start.expr, pattern.expr)
    elif isinstance(start, Num) and isinstance(pattern, Num): 
        pass
    else:
        return False  #Technically impossible situation        


    if pattern.token.type == MatcherWildcard:
        return result #We dont care about type of the start node

    result &= start.token.type == pattern.token.type 

    #base case
    return result