
from equation_parser import AST, BinOp, UnaryOp
from lexer import TokenType
from pattern_matcher import AnyOp, create_compound_binop, match
from utils import create_mul_op, create_num, create_plus_op, create_pow_op, create_sym, inorder, replace


class CollectionException(Exception):
    pass


def collect_numbers(op: BinOp) -> bool:
    """Searches for the following pattern in the code
        and applies rule:
        n (+ or - or * or / or ^) m -> o

        returns True if operation was executed
    """

    try:
        # Search rule:
        if not (op.token.type in {TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV, TokenType.POW}
                and op.left.token.type == TokenType.NUM
                and op.right.token.type == TokenType.NUM):
            return False
    except AttributeError:
        return False

    # define concrete operation dict
    op_dict = {
        TokenType.PLUS: lambda x, y: x + y,
        TokenType.MINUS: lambda x, y: x - y,
        TokenType.MUL: lambda x, y: x * y,
        TokenType.DIV: lambda x, y: x / y,
        TokenType.POW: lambda x, y: x ** y
    }

    # apply rule
    l = op.left
    r = op.right
    num = create_num(op_dict[op.token.type](l.value, r.value), op.parent)

    # change references
    if isinstance(op.parent, UnaryOp):
        op.parent.expr = num
    elif isinstance(op.parent, BinOp):
        if op.isLeft():
            op.parent.left = num
        else:
            op.parent.right = num
    else:
        raise CollectionException(
            f"Tree in bad state, cannot reassign child references from type {type(op.parent)}")
    return True


def collect_add_sub_same_symbols(op: BinOp):
    """Searches for the following pattern in the code
        and applies rule:
        x (+ or -) x -> x / Nothing

        returns True if operation was executed
    """

    try:
        # Search rule:
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

    # change refrences to the new token
    if isinstance(op.parent, UnaryOp):
        op.parent.expr = new_tok
    elif isinstance(op.parent, BinOp):
        if op.isLeft():
            op.parent.left = new_tok
        else:
            op.parent.right = new_tok
    else:
        raise CollectionException(
            f"Tree in bad state, cannot reassign child references from type {type(op.parent)}")
    return True


def collect_add_sub_same_symbols_pow_mul_nums(op: BinOp) -> bool:
    """Searches for the following pattern in code and applies rule:
        n*X^a +/- m*X^a --> (m+n)*X^a"""

    pattern = create_compound_binop({TokenType.PLUS, TokenType.MINUS},
                                    left=create_mul_op(
        left=create_num(),
        right=create_pow_op(
            left=create_sym(),
            right=create_num(),
        )
    ),
        right=create_mul_op(
            left=create_num(),
            right=create_pow_op(
                left=create_sym(),
                right=create_num(),
            )))

    if not match(op, pattern):
        return False

    # See if powers are the same
    if op.left.right.right.value != op.right.right.right.value:
        return False

    # See if symbols are the same
    if op.left.right.left.value != op.right.right.left.value:
        return False

    n = op.left.left.value
    m = op.right.left.value
    sym = op.left.right.left.value
    power = op.left.right.right.value

    multiplier = n+m if op.token.type == TokenType.PLUS else n-m

    # create replacement
    if multiplier != 0:
        new_op = create_mul_op(
            left=create_num(multiplier),
            right=create_pow_op(
                left=create_sym(sym),
                right=create_num(power)
            )
        )

        replace(op, new_op)
    else:
        replace(op, create_num(0))
    return True

# Collection search and rewrite rules


def collect_add_sub_same_symbols_mul_nums(op: BinOp) -> bool:
    """Searches for the following pattern in the code
        and applies rule:
        nX (+ or -) mX -> (m+n)X

        returns True if operation was executed
    """

    # search rule:
    try:
        r = op.right
        l = op.left
        rr = op.right.right
        rl = op.right.left
        lr = op.left.right
        ll = op.left.left

        # Node type and existance check
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

        # Symbol equality check
        symbol_right = rr if rr.token.type == TokenType.SYM else rl
        symbol_left = ll if ll.token.type == TokenType.SYM else lr

        if not symbol_left.value == symbol_right.value:
            return False

    except AttributeError:
        # catch nodes that do not exists and therefore do not conform
        # to search spec
        return False

    # Dictionary for concreate functions
    op_dict = {
        TokenType.PLUS: lambda x, y: x + y,
        TokenType.MINUS: lambda x, y: x - y,
    }

    # determine where are the numbers
    left_num = lr if symbol_left == ll else ll
    right_num = rl if symbol_right == rr else rr
    left_num = left_num.value
    right_num = right_num.value

    # apply rule
    num = create_num(op_dict[op.token.type](left_num, right_num))
    sym = create_sym(symbol_left.value)
    new_op = create_mul_op(
        left=num,
        right=sym,
        parent=op.parent)

    # change references
    if isinstance(op.parent, UnaryOp):
        op.parent.expr = new_op
    elif isinstance(op.parent, BinOp):
        if op.isLeft():
            op.parent.left = new_op
        else:
            op.parent.right = new_op
    else:
        raise CollectionException(
            f"Tree in bad state, cannot reassign child references from type {type(op.parent)}")
    return True


# Collection search and rewrite rules
def collect_mul_div_same_symbols(op: BinOp) -> bool:
    """Searches for the following pattern in the code
        and applies rule:
        X * X -> X^2
        X / X -> 1
        returns True if operation was executed
    """

    # Search for the following patterns:
    #     */
    #    /  \
    #  SYM  SYM

    pattern = create_compound_binop({TokenType.MUL, TokenType.DIV},
                                    left=create_sym("ANY"),
                                    right=create_sym("ANY"))

    if not match(op, pattern):
        return False

    if not op.left.value == op.right.value:
        return False

    symbol = op.left.value

    if op.token.type == TokenType.DIV:
        new_op = create_num(1, op.parent)
    else:
        # Create POW op
        new_op = create_pow_op(
            parent=op.parent,
            left=create_sym(symbol),
            right=create_num(2)
        )

    # Replace original op with POW op
    if isinstance(op.parent, UnaryOp):
        op.parent.expr = new_op
    elif isinstance(op.parent, BinOp):
        if op.isLeft():
            op.parent.left = new_op
        else:
            op.parent.right = new_op
    else:
        raise CollectionException(
            f"Tree in bad state, cannot reassign child references from type {type(op.parent)}")
    return True


def collect_mul_same_symbols_with_pows(op: BinOp) -> bool:
    """Searches for the following pattern in the code
        and applies rule:
        X^n * X^m -> X^(n+m)
        X^n / X^m -> X^(n-m)
        returns True if operation was executed
    """

    # Search for the following patterns:
    #
    #          */
    #       /     \
    #      ^       ^
    #     / \     / \
    #   SYM NUM SYM NUM

    pattern = create_compound_binop({TokenType.MUL, TokenType.DIV},
                                    left=create_pow_op(
        left=create_sym(),
        right=create_num()
    ),
        right=create_pow_op(
        left=create_sym(),
        right=create_num()
    ))

    if not match(op, pattern):
        return False

    # Symbol equality check
    if not op.left.left.value == op.right.left.value:
        return False

    symbol = op.left.left.value

    if op.token.type == TokenType.MUL:
        # what about unary minus here????
        new_op = create_pow_op(
            parent=op.parent,
            left=create_sym(symbol),
            right=create_num(op.left.right.value + op.right.right.value)
        )
    else:
        # what about unary minus here????
        new_op = create_pow_op(
            parent=op.parent,
            left=create_sym(symbol),
            right=create_num(op.left.right.value - op.right.right.value)
        )

    # Replace original op with POW op
    if isinstance(op.parent, UnaryOp):
        op.parent.expr = new_op
    elif isinstance(op.parent, BinOp):
        if op.isLeft():
            op.parent.left = new_op
        else:
            op.parent.right = new_op
    else:
        raise CollectionException(
            f"Tree in bad state, cannot reassign child references from type {type(op.parent)}")
    return True


def collect(root: AST):
    """Applies collection rewrite rules to reduce count of variables and numbers"""
    collection_functions = [collect_numbers, collect_mul_same_symbols_with_pows, collect_add_sub_same_symbols_mul_nums,
                            collect_add_sub_same_symbols, collect_mul_div_same_symbols, collect_add_sub_same_symbols_pow_mul_nums]
    rerun = True
    while rerun:
        rerun = False
        for f in collection_functions:
            tree_inord = inorder(root)
            for node in tree_inord:
                rerun |= f(node)
