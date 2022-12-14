from functools import reduce
from typing import List
from lexer import Token, TokenType
from equation_parser import AST, BinOp, Num, UnaryOp


def inorder(tree: AST) -> List[AST]:
    result = []
    if isinstance(tree, BinOp):
        result.extend(inorder(tree.left))
        result.append(tree)
        result.extend(inorder(tree.right))
    else:
        result.append(tree)
    return result

def preorder(tree: AST):
    pass

def postorder(tree: AST):
    pass


#TODO: Remove redundant parenthesis
def trace(root : AST) -> str:
    #HACK: Parenthesis removal
    result = _trace(root)
    return result[1:-1] 

def _trace(root : AST) -> str:
    """Creates human readable equation from AST"""
    result = []
    if isinstance(root, BinOp):
        result.append('(')
        result.extend(_trace(root.left))
        result.append(root.op.value)
        result.extend(_trace(root.right))
        result.append(")")
    elif isinstance(root, UnaryOp):
        result.append(root.op.value)
        result.append(_trace(root.expr))
    else:
        result.append(str(root.value))
    return ''.join(result)

#Node creation utility functions
#TODO: add tests for those functions
def create_plus_op(left: AST, right: AST, parent: AST | None = None) -> BinOp:
    return BinOp(left, Token('+', TokenType.PLUS), right, parent)

def create_minus_op(left: AST, right: AST, parent: AST | None = None) -> BinOp:
    return BinOp(left, Token('-', TokenType.MINUS), right, parent)

def create_mul_op(left: AST, right: AST, parent: AST | None = None) -> BinOp:
    return BinOp(left, Token('*', TokenType.MUL), right, parent)

def create_div_op(left: AST, right: AST, parent: AST | None = None) -> BinOp:
    return BinOp(left, Token('/', TokenType.DIV), right, parent)

def create_num(num: int | float = 0, parent: AST | None = None) -> Num:
    return Num(Token(num, TokenType.NUM), parent)

def create_sym(sym: int | float | str, parent: AST | None = None) -> Num:
    return Num(Token(sym, TokenType.SYM), parent)

def create_minus_unary(expr: AST, parent : AST | None = None):
    return UnaryOp(expr, Token('-', TokenType.MINUS), parent)

def add_unary_minus(node: AST):
    """Adds unary minus to target node, placing unary minus node in-between
    parent node and target node"""
    parent = node.parent
    op = create_minus_unary(node, node.parent)
    if isinstance(parent, UnaryOp):
        parent.expr = op
    elif node.isLeft():
        parent.left = op
    else:
        parent.right = op
    parent = op

def replace_node(node: AST, new_node: AST):
    """Replaces node with new_node
        This operation only makes sense if node and new_node
        are of the same type
    """

    if type(node) != type(new_node):
        raise Exception(f"Node replacement must operate on the same node types. Tried to exchange {type(node)} with {type(new_node)}")

    #replace parent references
    parent = node.parent
    if isinstance(parent, UnaryOp):
        parent.expr = new_node
    elif node.isLeft():
        parent.left = new_node
    else:
        parent.right = new_node

    #replace child references
    if isinstance(node, BinOp):
        l = node.left
        r = node.right

        new_node.left = l
        new_node.right = r

        if l:
            l.parent = new_node
        if r: 
            r.parent = new_node
    elif isinstance(node, UnaryOp):
        expr = node.expr
        new_node.expr = expr
        if expr:
            expr.parent = new_node
        
    


def test_inorder():
    #    1
    #    /\   
    #   /  \ 
    #  2    5
    # / \  / \
    #3   4 6  7 
    tree = BinOp(BinOp(Num(Token(3, None)), Token(2, None), Num(Token(4, None))), Token(1, None), BinOp(Num(Token(6, None)), Token(5, None), Num(Token(7, None))))
    result = inorder(tree)
    result = list(map(lambda x: x.token.value, result))
    assert [3, 2, 4, 1, 6, 5, 7] == result

def test_trace():
    # 2 + a = b * c
    #    =
    #    /\   
    #   /  \ 
    #  +    *
    # / \  / \
    #2   a b  c 
    test_str = "2 + a = b * c"
    tree = BinOp(BinOp(Num(Token(2, None)), Token("+", None), Num(Token("a", None))), Token("=", None), BinOp(Num(Token("b", None)), Token("*", None), Num(Token("c", None))))
    assert test_str == trace(tree)
