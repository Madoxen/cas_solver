from copy import deepcopy
from equation_parser import AST
from utils import inorder



#x+y+x -> x+x+y


def attract(root: AST):
    """Applies attraction rewrite rules to bring same symbol nodes
    closer together, if rewrite rule decreases amount of arcs between variables/number nodes
    it will be applied otherwise skipped"""
    
    copied_tree = deepcopy(root)
    attraction_functions = []
    rerun = True
    while rerun:
        rerun = False
        for f in attraction_functions:
            tree_inord = inorder(root)
            for node in tree_inord:
                rerun |= f(node)

    pass