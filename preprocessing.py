from copy import copy
from equation_parser import AST, BinOp, UnaryOp, parse
from lexer import TokenType
from pattern_matcher import AnyOp, create_compound_unary, match
from utils import create_minus_op, create_minus_unary, create_mul_op, create_num, create_plus_op, create_pow_op, create_sym, inorder, replace, trace

# Each found symbol must adhere to the following structure
#     *
#    / \
#   ANY ^
#      / \
#     x  ANY


class PreprocessingException(Exception):
    pass


def preprocess_plus_unary_minus(start_node: AST):
    """Changes occurences of unary minus and plus into binary minus"""
    # Find any +-
    pattern = create_plus_op(
        left=AnyOp(),
        right=create_minus_unary(expr=AnyOp()))

    if not match(start_node, pattern):
        return False

    # Turn +- into binary -
    new_op = create_minus_op(
        left=start_node.left,
        right=start_node.right.expr,
        parent=start_node.parent)
    # Replace OP
    replace(start_node, new_op)
    return True

def preprocess_unary_minus_plus(start_node: AST):
    """Changes occurences of unary minus and plus into binary minus"""
    # Find any +-
    pattern = create_plus_op(
        left=create_minus_unary(expr=AnyOp()),
        right=AnyOp())

    if not match(start_node, pattern):
        return False

    # Turn +- into binary -
    new_op = create_minus_op(
        left=start_node.left.expr,
        right=start_node.right,
        parent=start_node.parent)
    # Replace OP
    replace(start_node, new_op)
    return True



def preprocess_minus_unary_minus(start_node: AST):
    """Changes occurences of unary minus and plus into binary minus"""
    pattern = create_minus_op(
        left=AnyOp(),
        right=create_minus_unary(expr=AnyOp())
    )

    if not match(start_node, pattern):
        return False

    #turn -- into binary + 
    new_op = create_plus_op(
        left=start_node.left,
        right=start_node.right.expr,
        parent=start_node.parent)
    # Replace OP
    replace(start_node, new_op)
    return True

def preprocess_symbols_without_multiplication(start_node: AST):
    """Preprocesses symbol nodes that are not being multiplied
    so that they will be transformed into 1*x"""

    pattern = create_pow_op(
        left=create_sym(),
        right=create_num())

    if not match(start_node, pattern):
        return False

    if start_node.parent == None:
        return False

    if start_node.parent.token.type == TokenType.MUL:
        return False

    # inject 1* op
    new_op = create_mul_op(
        left=create_num(1),
        right=copy(start_node),
        parent=start_node.parent)

    replace(start_node, new_op)
    return True


def preprocess_symbols_without_power(start_node: AST):
    pattern = create_sym()

    if not match(start_node, pattern):
        return False

    if start_node.parent == None:
        return False

    if start_node.parent.token.type == TokenType.POW:
        return False

    # inject ^1 op
    new_op = create_pow_op(
        left=copy(start_node),
        right=create_num(1),
        parent=start_node.parent)

    replace(start_node, new_op)
    return True


def preprocess(root: AST):
    """Applies preprocessing to allow execution of some rules in attraction and collection modules
    without preprocessing, we would have to write many additional rules"""
    collection_functions = [preprocess_plus_unary_minus,
                            preprocess_symbols_without_power, preprocess_symbols_without_multiplication, preprocess_minus_unary_minus,preprocess_unary_minus_plus]
                        
    rerun = True
    while rerun:
        rerun = False
        for f in collection_functions:
            tree_inord = inorder(root)
            for node in tree_inord:
                rerun |= f(node)
    print(trace(root))
