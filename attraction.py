from copy import deepcopy
from equation_parser import AST, BinOp
from lexer import TokenType, Token
from utils import create_graphviz_graph, inorder, distance, swap, trace
from itertools import combinations, groupby, pairwise, permutations
from pattern_matcher import AnyOp, create_compound_binop, match

# x+y+x -> x+x+y
def attract_add_sub_mul(start_node: AST) -> bool:
    # search for pattern from start node
    # The following pattern is searched
    #        +-            +-
    #       / \           / \
    #      +-  c   OR    c   +-
    #     / \               / \
    #    a   b             a   b
    #              OR
    #        *              *
    #       / \            / \
    #      *  c    OR    c    *
    #     / \                / \
    #    a   b              a   b
    try:
        # Search rule:
        left_sided_pattern = create_compound_binop({TokenType.PLUS, TokenType.MINUS},
                                                   left=create_compound_binop(
                                                       {TokenType.PLUS, TokenType.MINUS}, left=AnyOp(), right=AnyOp()),
                                                   right=AnyOp())
        right_sided_pattern = create_compound_binop({TokenType.PLUS, TokenType.MINUS},
                                                    left=AnyOp(),
                                                    right=create_compound_binop({TokenType.PLUS, TokenType.MINUS}, left=AnyOp(), right=AnyOp()))

        left_sided_pattern_mul = create_compound_binop({TokenType.MUL},
                                                       left=create_compound_binop(
                                                           {TokenType.MUL}, left=AnyOp(), right=AnyOp()),
                                                       right=AnyOp())

        right_sided_pattern_mul = create_compound_binop({TokenType.MUL},
                                                        left=AnyOp(),
                                                        right=create_compound_binop({TokenType.MUL}, left=AnyOp(), right=AnyOp()))

        left_sided = match(start_node, left_sided_pattern)
        right_sided = match(start_node, right_sided_pattern)

        left_sided_mul = match(start_node, left_sided_pattern_mul)
        right_sided_mul = match(start_node, right_sided_pattern_mul)

        left_sided = left_sided or left_sided_mul
        right_sided = right_sided or right_sided_mul

        if (left_sided or right_sided) == False:
            return False
    except AttributeError:
        return False

    # Find unknowns in the subtrees of the start_node
    sn_inord = inorder(start_node)
    unknowns = [x for x in sn_inord if x.token.type == TokenType.SYM]
    # Group unknowns by value
    unknowns = list(sorted(unknowns, key=lambda x: x.token.value))
    unknowns = [list(g) for k, g in groupby(
        unknowns, key=lambda x: x.token.value)]

    if len(unknowns) == 0:
        return False
    # Focus on unknowns that have the most nodes in the tree
    unknowns = max(unknowns, key=lambda x: len(x))

    # Compute distance array
    unknowns_distances = [distance(x, y) for x, y in combinations(unknowns, 2)]

    for far in [False, True]:
        # Apply transformation
        if left_sided:
            if not far:
                swap(start_node.left.right, start_node.right)
            else:
                swap(start_node.left.left, start_node.right)
        else:
            if not far:
                swap(start_node.right.left, start_node.left)
            else:
                swap(start_node.right.right, start_node.left)

        # calculate distances again and compare
        new_unknowns_distances = [distance(x, y)
                                  for x, y in combinations(unknowns, 2)]

        # calculate distance change, if there is at least one negative change (so the two occurences of the same
        # variable are closer) accept the change, otherwise reverse changes to the tree
        distance_difference = []
        for old_dist, new_dist in zip(unknowns_distances, new_unknowns_distances):
            distance_difference.append(new_dist - old_dist)

        success = sum(distance_difference) < 0

        if not success:
            # reverse transformation
            if left_sided:
                if not far:
                    swap(start_node.left.right, start_node.right)
                else:
                    swap(start_node.left.left, start_node.right)
            else:
                if not far:
                    swap(start_node.right.left, start_node.left)
                else:
                    swap(start_node.right.right, start_node.left)
        else:
            break
    return success


def attract(root: AST):
    """Applies attraction rewrite rules to bring same symbol nodes
    closer together, if rewrite rule decreases amount of arcs between variables/number nodes
    it will be applied otherwise skipped"""

    attraction_functions = [attract_add_sub_mul]
    rerun = True
    while rerun:
        rerun = False
        for f in attraction_functions:
            tree_inord = inorder(root)
            for node in tree_inord:
                rerun |= f(node)
