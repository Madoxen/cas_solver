from attraction import attract
from collection import collect
from equation_parser import AST
from isolation import isolate


def solve(root: AST):
    attract(root)
    collect(root)
    isolate(root)
    return root
