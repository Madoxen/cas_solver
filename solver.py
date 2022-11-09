from parser import Parser
from lexer import TokenType


class Solver:
    def __init__(self,string: str):
        self.ast = Parser(string).parse()
    
    def solve(self, symbol: str):
        """Solves for given _symbol_"""

        #perform DFS to find requested symbol occurences
