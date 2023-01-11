from functools import reduce
from typing import List
from lexer import Token, TokenType
from equation_parser import AST, BinOp, Num, UnaryOp
import pygraphviz

def inorder(tree: AST) -> List[AST]:
    result = []
    if isinstance(tree, BinOp):
        result.extend(inorder(tree.left))
        result.append(tree)
        result.extend(inorder(tree.right))
    elif isinstance(tree, UnaryOp):
        result.extend(inorder(tree.expr))
        result.append(tree)
    else:
        result.append(tree)
    return result

def preorder(tree: AST):
    pass

def postorder(tree: AST):
    pass

def create_graphviz_graph(root: AST , path: str):
    G = pygraphviz.AGraph(directed=True)
    
    counter = 0
    lookup = {} 
    for n in inorder(root):
        lookup[n] = counter
        counter += 1
    
    for k,v in lookup.items():
        G.add_node(v, label=k.token.value)
        if isinstance(k, BinOp):
            if k.left:
                G.add_edge(v, lookup[k.left])
            if k.right:
                G.add_edge(v, lookup[k.right])
        elif isinstance(k, UnaryOp):
            G.add_edge(v, lookup[k.expr])
    G.layout(prog='dot')
    G.draw(path)


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
        isFunc = root.op.type == TokenType.FUNC
        result.append(root.op.value)
        if isFunc:
            result.append('(')
        result.append(_trace(root.expr))
        if isFunc:
            result.append(')')
    elif isinstance(root, Num):
        result.append(str(root.value))
    else:
        raise TypeError(f"Cannot trace tree, node type: {type(root)} not supported")
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

def create_pow_op(left: AST, right: AST, parent: AST | None = None) -> BinOp:
    result = BinOp(left, Token('^', TokenType.POW), right, parent)
    return result

def create_num(num: int | float = 0, parent: AST | None = None) -> Num:
    return Num(Token(num, TokenType.NUM), parent)

def create_sym(sym: int | float | str = "", parent: AST | None = None) -> Num:
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

def replace(original_op, new_op):
    """Replaces original_op with new_op and updateds parent references"""
    if isinstance(original_op.parent, UnaryOp):
        original_op.parent.expr = new_op
    elif isinstance(original_op.parent, BinOp):
        if original_op.isLeft():
            original_op.parent.left = new_op
        else:
            original_op.parent.right = new_op
    else:
        raise Exception(f"Cannot reassign child references from type {type(original_op.parent)}")
    if new_op != None:
        new_op.parent = original_op.parent


        
def swap(a: AST, b:AST):
    """Swaps two nodes positions in a tree (changes parent and parent links)"""
    #replace parent references
    a_parent = a.parent
    b_parent = b.parent
    if isinstance(a_parent, UnaryOp):
        a_parent.expr = b
    elif isinstance(a_parent, BinOp):
        if a.isLeft():
            a_parent.left = b
        else:
            a_parent.right = b
    a.parent = b_parent

    if isinstance(b_parent, UnaryOp):
        b_parent.expr = a
    elif isinstance(b_parent, BinOp):
        if b.isLeft():
            b_parent.left = a
        else:
            b_parent.right = a
    b.parent = a_parent

    


    
def distance(a: AST, b: AST) -> int | None:
    """Calculates distance (number of arcs) between two nodes in a tree
    returns None if there is no path between two nodes"""
    if a == b:
        return 0 

    curr_a = a
    curr_b = b

    a_path = []
    b_path = []
    while curr_a != curr_b:
        if curr_a.parent != None: #check if root was reached
            curr_a = curr_a.parent #move up
            a_path.append(curr_a)
        if curr_b.parent != None:
            curr_b = curr_b.parent
            b_path.append(curr_b)
        if curr_a == b:
            return len(a_path) #b is higher than a, return 
        if curr_b == a:
            return len(b_path) #a is higher than b, return
    

    b_set = set(b_path)

    a_idx = None
    earliest_node = None
    for idx, a_node in enumerate(a_path):
        if a_node in b_set:
            a_idx = idx
            earliest_node = a_node
            break

    if a_idx == None:
        return None

    #find path length to common earliest intersection
    b_idx = b_path.index(earliest_node)
    #The distance between two nodes in a tree is the sum of length of their
    #paths to the earliest intersection parent. We add +2 to account for python
    #0-based indexing
    return a_idx + b_idx + 2 


