
from equation_parser import AST, BinOp, UnaryOp
from lexer import TokenType
from utils import create_mul_op, create_num, create_sym, inorder


class CollectionException(Exception):
    pass

def collect_numbers(op: BinOp) -> bool:
    """Searches for the following pattern in the code
        and applies rule:
        n (+ or - or * or / or ^) m -> o

        returns True if operation was executed
    """

    try:
    #Search rule:
        if not (op.token.type in {TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV, TokenType.POW}
        and op.left.token.type == TokenType.NUM
        and op.right.token.type == TokenType.NUM):
            return False
    except AttributeError:
        return False

    #define concrete operation dict
    op_dict = {
        TokenType.PLUS : lambda x,y: x + y,
        TokenType.MINUS : lambda x,y: x - y,
        TokenType.MUL : lambda x,y: x * y,
        TokenType.DIV : lambda x,y: x / y,
        TokenType.POW : lambda x,y: x ** y
    }    
    
    #apply rule
    l = op.left
    r = op.right
    num = create_num(op_dict[op.token.type](l.value,r.value), op.parent)

    #change references
    if isinstance(op.parent, UnaryOp):
        op.parent.expr = num
    elif isinstance(op.parent, BinOp):
        if op.isLeft():
            op.parent.left = num
        else:
            op.parent.right = num
    else:
        raise CollectionException(f"Tree in bad state, cannot reassign child references from type {type(op.parent)}")
    return True 
     

def collect_add_sub_same_symbols(op: BinOp):
    """Searches for the following pattern in the code
        and applies rule:
        x (+ or -) x -> x / Nothing

        returns True if operation was executed
    """

    try:
    #Search rule:
        if not (op.token.type in {TokenType.PLUS, TokenType.MINUS}
        and op.left.token.type == TokenType.SYM
        and op.right.token.type == TokenType.SYM
        and op.left.token.value == op.right.token.value):
            return False
    except AttributeError:
        return False

    new_tok = None
    if op.token.type == TokenType.PLUS:
        new_tok = create_mul_op(create_num(2), create_sym("x"), op.parent)
    else: 
        new_tok = create_num(0, op.parent)

    #change refrences to the new token
    if isinstance(op.parent, UnaryOp):
        op.parent.expr = new_tok
    elif isinstance(op.parent, BinOp):
        if op.isLeft():
            op.parent.left = new_tok
        else:
            op.parent.right = new_tok
    else:
        raise CollectionException(f"Tree in bad state, cannot reassign child references from type {type(op.parent)}")
    return True 


#Collection search and rewrite rules
def collect_add_sub_same_symbols_mul_nums(op: BinOp) -> bool:
    """Searches for the following pattern in the code
        and applies rule:
        nX (+ or -) mX -> (m+n)X

        returns True if operation was executed
    """

    #search rule:
    try:
        r = op.right
        l = op.left
        rr = op.right.right
        rl = op.right.left
        lr = op.left.right
        ll = op.left.left

        #Node type and existance check
        if not (op.token.type in {TokenType.PLUS, TokenType.MINUS}
        and l.token.type in {TokenType.MUL, TokenType.DIV}
        and r.token.type in {TokenType.MUL, TokenType.DIV}
        and lr.token.type in {TokenType.SYM, TokenType.NUM}
        and ll.token.type in {TokenType.SYM, TokenType.NUM}
        and rr.token.type in {TokenType.SYM, TokenType.NUM}
        and rl.token.type in {TokenType.SYM, TokenType.NUM}
        and rl.token.type != rr.token.type
        and ll.token.type != lr.token.type):
            return False
        
        #Symbol equality check
        symbol_right = rr if rr.token.type == TokenType.SYM else rl 
        symbol_left = ll if ll.token.type == TokenType.SYM else lr
        
        if not symbol_left.value == symbol_right.value:
            return False

    except AttributeError:
        #catch nodes that do not exists and therefore do not conform 
        #to search spec 
        return False

    #Dictionary for concreate functions
    op_dict = {
        TokenType.PLUS : lambda x,y: x + y,
        TokenType.MINUS : lambda x,y: x - y,
    }


    #determine where are the numbers
    left_num = lr if symbol_left == ll else ll
    right_num = rl if symbol_right == rr else rr
    left_num = left_num.value
    right_num = right_num.value

    #apply rule 
    num = create_num(op_dict[op.token.type](left_num, right_num))
    sym = create_sym(symbol_left.value)
    new_op = create_mul_op(num, sym, op.parent)
    
    
    #change references
    if isinstance(op.parent, UnaryOp):
        op.parent.expr = new_op
    elif isinstance(op.parent, BinOp):
        if op.isLeft():
            op.parent.left = new_op
        else:
            op.parent.right = new_op
    else:
        raise CollectionException(f"Tree in bad state, cannot reassign child references from type {type(op.parent)}")
    return True 

    

#Collection search and rewrite rules
def collect_mul_div_same_symbols(op: BinOp) -> bool:
    """Searches for the following pattern in the code
        and applies rule:
        nX + mX -> (m+n)X
        returns True if operation was executed
    """
    search_pattern = BinOp()


def collect(root: AST):
    """Applies collection rewrite rules to reduce count of variables and numbers"""
    collection_functions = [collect_numbers, collect_add_sub_same_symbols_mul_nums, collect_add_sub_same_symbols]
    rerun = True
    while rerun:
        rerun = False
        for f in collection_functions:
            tree_inord = inorder(root)
            for node in tree_inord:
                rerun |= f(node)

