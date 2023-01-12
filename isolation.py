from typing import List
from attraction import attract
from equation_parser import AST, BinOp, Num, Parser, UnaryOp
from lexer import Lexer, TokenType, Token
from postprocessing import postprocess
from preprocessing import preprocess
from utils import add_unary_minus, create_div_op, create_graphviz_graph, create_mul_op, create_num, create_plus_op, create_sym, trace, inorder
from collection import collect
import math


# TODO: improve doc strings because they are misleading
# TODO: build in move operation and add checks against
# not supported moves

def pow_inv(n: BinOp, wasTargetLeft: bool):
    """
        Inverses the power operation in the following way: 
        Target - A: A ^ B = C ---> A = C ^ (1/B)
        Target - B: NOT SUPPORTED (throws exception)
        Only left side target is allowed
    """

    if not wasTargetLeft:
        raise SolverException("Left target power inverse is not supported")

    # invert exponent E --> 1/E
    numerator = Num(Token(1, TokenType.NUM), None)
    denominator = n.right
    inverted_exponent = create_div_op(numerator, denominator, n)
    n.right = inverted_exponent


def div_inv(n: BinOp, wasTargetLeft: bool):
    """
    Target - A:  A / B = C ---> A = C * B 
    Target - B:  A / B = C ---> B = B / C 
    """

    if not wasTargetLeft:
        # switch right side with left
        n.right, n.left = n.left, n.right
    else:
        # change the op to multiplication
        n.op.type = TokenType.MUL
        n.op.value = "*"


def mul_inv(n: BinOp, wasTargetLeft: bool):
    """Target - A: A * B = C ---> A = C / B
    Target - B: A * B = C ---> B = C / A"""
    n.op.type = TokenType.DIV
    n.op.value = "/"


def add_inv(n: BinOp, wasTargetLeft: bool):
    """Target - A: A + B = C ---> A = C - B
    Target - B: A + B = C ---> B =  C - A"""
    n.op.type = TokenType.MINUS
    n.op.value = "-"


def sub_inv(n: BinOp, wasTargetLeft: bool):
    """Target - A (wasTargetLeft == True): A - B = C ---> A = C + B
    Target - B: A - B = C ---> B = -(C + A) ---> -C + A"""

    if not wasTargetLeft:
        # if target was left this means that C is on the left side
        # Add unary to the left side
        min_tok = Token("-", TokenType.MINUS)
        min_uop = UnaryOp(n.left, min_tok, n)
        n.left = min_uop

    n.op.type = TokenType.PLUS
    n.op.value = "+"


def sin_inv(n: UnaryOp):
    n.op.value = "asin"


def cos_inv(n: UnaryOp):
    n.op.value = "acos"


def tan_inv(n: UnaryOp):
    n.op.value = "atan"


def asin_inv(n: UnaryOp):
    n.op.value = "sin"


def acos_inv(n: UnaryOp):
    n.op.value = "cos"


def atan_inv(n: UnaryOp):
    n.op.value = "tan"


class SolverException(Exception):
    pass


class Solver:
    def __init__(self, string: str):
        self.root = Parser(string).parse()

    def solve(self, symbol: str) -> AST:
        """Solves for given _searched symbol_
        Solving is essentialy a process of moving all non _searched symbol_ nodes to the right side of the tree
        while having all _searched symbol_ nodes on the left side. This needs to be done with rules of algebra"""

        # note: maybe if there is no equals sign, just add "= 0" to the end of equation?
        if self.root.op.type != TokenType.EQ:
            raise SolverException(
                "Provided expression tree does not contain '=' at root element")

        preprocess(self.root)
        print("preprocess", trace(self.root))
        attract(self.root)
        print("attract", trace(self.root))
        collect(self.root)
        print("collect", trace(self.root))
        postprocess(self.root)
        print("postprocess", trace(self.root))
        # perform DFS to find requested symbol occurences
        # TODO: make sure that left and right subtree are NOT None!!
        left_subtree_snodes = self.dfs(symbol, self.root.left)
        right_subtree_snodes = self.dfs(symbol, self.root.right)

        # swap left with right if there are more searched symbols on the right side
        if len(right_subtree_snodes) > len(left_subtree_snodes):
            self.root.left, self.root.right = self.root.right, self.root.left
            left_subtree_snodes, right_subtree_snodes = right_subtree_snodes, left_subtree_snodes

        if len(right_subtree_snodes) == 0 and len(left_subtree_snodes) == 0:
            raise SolverException(
                "Searched symbol was not found in the provided equation")

        if len(left_subtree_snodes) > 1:
            raise SolverException(
                "Multiple unknown occurences after initial collection, solving not supported")

        # 1. Get all searched symbols to the left side
        # 2. Get all not-searched symbols to the right side
            # - We can only move symbols from the top of the subtree
            # to the top of second subtree to respect execution order
            # - To respect mathematical rules of basic algebra
            # we must use transformations defined in a transformation set
            #
            # Start by finding searched symbol in
            #  the subtree
            # some inspiration: https://stackoverflow.com/a/66466263

        # TODO: support trig functions and their inverses
        inverse_binops = {
            TokenType.DIV: div_inv,
            TokenType.MUL: mul_inv,
            TokenType.PLUS: add_inv,
            TokenType.MINUS: sub_inv,
            TokenType.POW: pow_inv
        }

        inverse_unaryops = {
            "sin": sin_inv,
            "cos": cos_inv,
            "tan": tan_inv,
            "asin": asin_inv,
            "acos": acos_inv,
            "atan": atan_inv,
        }

        # Glossary:
        # OP - short for operation (+, -, *, sin() etc.)
        # snode - searched node eg. the node that we search for

        # go through all searched nodes
        # Move everything that is not an snode
        for snode in left_subtree_snodes:
            path = list(reversed(self.path(snode)))
            for n, n2 in zip(path, path[1:]):
                if n.token.type == TokenType.EQ:  # skip equals
                    continue

                # determine if current node is left or right
                # node of the parent
                isLeft = n.isLeft()

                if isinstance(n, UnaryOp):
                    # move symbol and the subtree that
                    # does not have snode in it to the right
                    # inverting the op
                    # Attach the moved inverted op as a root
                    # of the right subtree

                    # save reference for old right root child
                    root_right = self.root.right
                    # Searched node is in the expression of the unary operator
                    if n2 == n.expr:
                        # leave rest of expression intact
                        # since snode is in there
                        if isLeft:
                            n.parent.left = n.expr
                        else:
                            n.parent.right = n.expr
                        n.expr.parent = n.parent

                        # bypass UnaryOps with PLUS op
                        if n.op.type == TokenType.PLUS:
                            continue

                        # TODO: other unary functions and ops have to be
                        # inversed
                        # Invert op for all UnaryOps except of MINUS op which
                        # simply is moved to the right of the root
                        if n.op.type != TokenType.MINUS:
                            inv_op = inverse_unaryops.get(n.op.value, False)
                            if not inv_op:
                                raise SolverException(
                                    f"Could not find inverse operation for: {n.op.value}")
                            inv_op(n)

                        # move op to the right of the root
                        n.parent = self.root
                        n.expr = self.root.right
                        self.root.right = n

                    else:
                        pass

                elif isinstance(n, BinOp):
                    # move symbol and the subtree that
                    # does not have snode in it to the right
                    # inverting the op
                    # Attach the moved inverted op as a root
                    # of the right subtree, and attach
                    # the right subtree as a left child of moved
                    # inverted op

                    # save reference for old right root child
                    root_right = self.root.right
                    # choose subtree
                    if n.right == n2:
                        isTargetLeft = False
                        # snode is in right subtree
                        # leave right subtree behind
                        n.right.parent = n.parent
                        if isLeft:
                            n.parent.left = n.right
                        else:
                            n.parent.right = n.right

                        # move left subtree to the right
                        n.right = n.left
                        n.left = root_right
                    else:
                        isTargetLeft = True
                        # snode is in left subtree
                        # leave left subtree behind
                        n.left.parent = n.parent

                        # attach left subtree to correct parent subtree
                        if isLeft:
                            n.parent.left = n.left
                        else:
                            n.parent.right = n.left
                        # attach OP node left side to the root.right
                        n.left = root_right

                    n.parent = self.root
                    root_right.parent = n
                    self.root.right = n

                    # Inverse the OP
                    inv_op = inverse_binops.get(n.op.type, False)
                    if not inv_op:
                        raise SolverException(
                            f"Could not find inverse operation for: {n.op.type}")
                    inv_op(n, isTargetLeft)

        print("isolate", trace(self.root))
        # Postprocessing
        preprocess(self.root)
        print("preprocess", trace(self.root))
        attract(self.root)
        print("attract", trace(self.root))
        collect(self.root)
        print("collect", trace(self.root))
        postprocess(self.root)
        print("postprocess", trace(self.root))
        return self.root

    def dfs(self, symbol: str, start_point: AST = None) -> List[AST]:
        """Searches the ast tree
        Function assumes binary tree and no loops,
        if there are some, it will hang and destroy the universe"""
        if start_point == None:
            start_point = self.root
        result = []
        if isinstance(start_point, Num):
            if start_point.value == symbol:
                result.append(start_point)
        elif isinstance(start_point, BinOp):
            result.extend(self.dfs(symbol, start_point.left))
            result.extend(self.dfs(symbol, start_point.right))
        elif isinstance(start_point, UnaryOp):
            result.extend(self.dfs(symbol, start_point.expr))
        else:
            return []
        return result

    def path(self, start_point):
        result = []
        curr = start_point
        while curr != None:
            result.append(curr)
            curr = curr.parent
        return result
