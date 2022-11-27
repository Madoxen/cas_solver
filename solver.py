from typing import List
from parser import AST, BinOp, Num, Parser
from lexer import Lexer, TokenType
from utils import trace 

class SolverException(Exception):
    pass


class Solver:
    def __init__(self, string: str):
        self.root = Parser(string).parse()
        self.inv_map = {v: k for k, v in Lexer.operators.items()}

    def solve(self, symbol: str) -> AST:
        """Solves for given _searched symbol_
        Solving is essentialy a process of moving all non _searched symbol_ nodes to the right side of the tree
        while having all _searched symbol_ nodes on the left side. This needs to be done with rules of algebra"""

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
            # - We can only move symbols from the top of the subtree
            # to the top of second subtree to respect execution order
            # - To respect mathematical rules of basic algebra
            # we must use transformations defined in a transformation set
            #
            # Start by finding searched symbol in the subtree
            #some inspiration: https://stackoverflow.com/a/66466263

        #TODO: support multiple searched nodes 
        #1. find symbol that we are intrested in
        target_node = left_subtree_syms[0]

        inverse_op = {
            TokenType.DIV : TokenType.MUL,
            TokenType.MUL : TokenType.DIV,
            TokenType.PLUS : TokenType.MINUS,
            TokenType.MINUS : TokenType.PLUS,
        }

        #continue as long as on the left we will have only
        #the target node
        while self.root.left != target_node:

            #move OP and it's left subtree to the right side
            op = self.root.left
            r = self.root.right
            if op.right == target_node:
                self.root.left = op.right
                op.right = r
            else:
                self.root.left = op.left
                op.left = r
                
            
            
            self.root.right = op
        
            #Inverse the OP
            op.op.type = inverse_op[op.op.type]
            op.op.value = self.inv_map[op.op.type]


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
        else:
            return []  # we should throw exception here really...
        return result

if __name__ == "__main__":
    s = Solver("(a+b)*c-7 = 1")
    print(trace(s.solve("a")))
    
