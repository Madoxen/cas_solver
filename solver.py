from parser import Parser
from lexer import TokenType


class Solver:
    def __init__(self,string: str):
        self.ast = Parser(string).parse()
    
    def solve(self, symbol: str):
        """Solves for given _symbol_
        Solving is essentialy a process of moving all non _symbol_ nodes to the right side of the tree
        while having all _symbol_ nodes on the left side. This needs to be done with rules of algebra"""

        #perform DFS to find requested symbol occurences
