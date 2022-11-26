from typing import List
from parser import AST, BinOp, Num, Parser
from lexer import TokenType
from utils import inorder, trace 
from functools import reduce

class SolverException(Exception):
    pass


class Solver:
    def __init__(self, string: str):
        self.root = Parser(string).parse()

    def solve(self, symbol: str) -> str:
        """Solves for given _symbol_
        Solving is essentialy a process of moving all non _symbol_ nodes to the right side of the tree
        while having all _symbol_ nodes on the left side. This needs to be done with rules of algebra"""

        # note: maybe if there is no equals sign, just add "= 0" to the end of equation?
        if self.root.op.type != TokenType.EQ:
            raise SolverException("Provided string is not an equation")

        # perform DFS to find requested symbol occurences
        left_subtree_syms = self.dfs(symbol,self.root.left)
        right_subtree_syms = self.dfs(symbol,self.root.right)

        #swap left with right if there are more searched symbols on the right side
        if len(right_subtree_syms) > len(left_subtree_syms):
            self.root.left, self.root.right = self.root.right, self.root.left
            left_subtree_syms, right_subtree_syms = right_subtree_syms, left_subtree_syms

        #1. Get all searched symbols to the left side
        #2. Get all not-searched symbols to the right side
            

        return trace(self.root)
        

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
        else:
            return []  # we should throw exception here really...
        return result
