from copy import copy
from equation_parser import AST, BinOp, UnaryOp, parse
from lexer import TokenType
from pattern_matcher import AnyOp, create_compound_unary, match
from utils import create_minus_op, create_minus_unary, create_mul_op, create_num, create_plus_op, create_pow_op, create_sym, inorder, replace, trace

#Each found symbol must adhere to the following structure
#     *
#    / \
#   ANY ^
#      / \ 
#     x  ANY

class PreprocessingException(Exception):
    pass



def postprocess_trivial_mul(start_node: AST):
    if not isinstance(start_node, BinOp):
        return False #there is no unary or num mul

    pattern_right = create_mul_op(left=create_num(1), right=AnyOp())
    pattern_left = create_mul_op(left=AnyOp(), right=create_num(1))
    replacement = None 

    if match(start_node, pattern_right):
        replacement = start_node.right
    elif match(start_node, pattern_left):
        replacement = start_node.left
    else:
        return False

    replace(start_node, replacement)
    return True 


def postprocess_trivial_power(start_node: AST):
    if not isinstance(start_node, BinOp):
        return False #there is no unary or num mul

    pattern = create_pow_op(left=AnyOp(), right=create_num(1))
    replacement = None 

    if match(start_node, pattern):
        replacement = start_node.left
    else:
        return False

    replace(start_node, replacement)
    return True 



def postprocess(root: AST):
    """Applies post processing of the expression tree, things like 1*, ^1 excessive - signs will be removed since they do not affect the 
    overall equation"""
    collection_functions = [postprocess_trivial_mul, postprocess_trivial_power]
    rerun = True
    while rerun:
        rerun = False
        for f in collection_functions:
            tree_inord = inorder(root)
            for node in tree_inord:
                rerun |= f(node)

