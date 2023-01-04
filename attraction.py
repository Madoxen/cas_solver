from copy import deepcopy
from equation_parser import AST
from lexer import TokenType
from utils import create_graphviz_graph, inorder, distance, trace
from itertools import combinations, groupby, pairwise, permutations


# x+y+x -> x+x+y
def attract_addition(start_node: AST) -> bool:
    # search for pattern from start node
    # The following pattern is searched
    #        +-            +-
    #       / \           / \
    #      +-  c   OR    c   +-
    #     / \               / \
    #    a   b             a   b
    try:
        # Search rule:
        isLeftSided = (start_node.token.type in {TokenType.PLUS, TokenType.MINUS}
                       and start_node.left.token.type in {TokenType.PLUS, TokenType.MINUS}
                       and start_node.left.right != None
                       and start_node.left.left != None
                       and start_node.right != None)
        isRightSided = (start_node.token.type in {TokenType.PLUS, TokenType.MINUS}
                        and start_node.right.token.type in {TokenType.PLUS, TokenType.MINUS}
                        and start_node.right.right != None
                        and start_node.right.left != None
                        and start_node.left != None)
        if (isLeftSided or isRightSided) == False:
            return False
    except AttributeError:
        return False
    # Apply the rule to the copy and check if unknowns are closer together

    # Find unknowns in the subtrees of the start_node
    sn_inord = inorder(start_node)
    unknowns = [x for x in sn_inord if x.token.type == TokenType.SYM]
    # Group unknowns by value
    unknowns = list(sorted(unknowns, key=lambda x: x.token.value))
    unknowns = [list(g) for k, g in groupby(
        unknowns, key=lambda x: x.token.value)]

    # Focus on unknowns that have the most nodes in the tree
    unknowns = max(unknowns, key=lambda x: len(x)) 

    # this might explode in complexity!
    # Compute distance array
    unknowns_distances = [distance(x, y) for x,y in combinations(unknowns,2)] 

    # Apply transformation
    # replace b with c and c with b
    if isLeftSided:
        start_node.left.right.parent, start_node.right.parent = start_node.right.parent, start_node.left.right.parent
        start_node.left.right, start_node.right = start_node.right, start_node.left.right
    else:
        start_node.right.left.parent, start_node.left.parent = start_node.left.parent, start_node.right.left.parent
        start_node.right.left, start_node.left = start_node.left, start_node.right.left

    # calculate distances again and compare
    new_unknowns_distances = [distance(x, y) for x,y in combinations(unknowns,2)] 

    # calculate distance change, if there is at least one negative change (so the two occurences of the same
    # variable are closer) accept the change, otherwise reverse changes to the tree
    distance_difference = []
    for old_dist, new_dist in zip(unknowns_distances, new_unknowns_distances):
        distance_difference.append(new_dist - old_dist)

    success = any(x < 0 for x in distance_difference) 

    if not success:
        if isLeftSided:
            start_node.left.right.parent, start_node.right.parent = start_node.right.parent, start_node.left.right.parent
            start_node.left.right, start_node.right = start_node.right, start_node.left.right
        else:
            start_node.right.left.parent, start_node.left.parent = start_node.left.parent, start_node.right.left.parent
            start_node.right.left, start_node.left = start_node.left, start_node.right.left
    return success


def attract(root: AST):
    """Applies attraction rewrite rules to bring same symbol nodes
    closer together, if rewrite rule decreases amount of arcs between variables/number nodes
    it will be applied otherwise skipped"""

    attraction_functions = [attract_addition]
    rerun = True
    while rerun:
        rerun = False
        for f in attraction_functions:
            tree_inord = inorder(root)
            for node in tree_inord:
                rerun |= f(node)
