from typing import List
from parser import AST, BinOp, Num, Parser
from lexer import Lexer, TokenType
from utils import trace, inorder

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
        left_subtree_snodes = self.dfs(symbol,self.root.left)
        right_subtree_snodes = self.dfs(symbol,self.root.right)

        #swap left with right if there are more searched symbols on the right side
        if len(right_subtree_snodes) > len(left_subtree_snodes):
            self.root.left, self.root.right = self.root.right, self.root.left
            left_subtree_snodes, right_subtree_snodes = right_subtree_snodes, left_subtree_snodes

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
        target_node = left_subtree_snodes[0]

        inverse_op = {
            TokenType.DIV : TokenType.MUL,
            TokenType.MUL : TokenType.DIV,
            TokenType.PLUS : TokenType.MINUS,
            TokenType.MINUS : TokenType.PLUS,
        }

        # high level idea
        # get traces to the searched symbols
        # - along the trace apply inverse move to the right side
        # while choosing the appropiate subtrees that do not
        # contain the searched node (snode). Those subtrees
        # will be moved together with OP node

        #go through all searched nodes
        #Move everything that is not an snode
        for snode in left_subtree_snodes:
            path = list(reversed(self.path(snode)))
            print(list(map(lambda x: x.token.value, path)))
            for n, n2 in zip(path, path[1:]):
                if n.token.type == TokenType.EQ: #skip equals
                    continue

                #determine if current node is left or right
                #node of the parent
                isLeft = False 
                if n.parent.left == n:
                    isLeft = True

                #move symbol and the subtree that 
                #does not have snode in it to the right
                #inverting the op
                #Attach the moved inverted op as a root
                #of the right subtree, and attach
                #the right subtree as a left child of moved
                #inverted op 
                
                root_right = self.root.right
                #choose subtree
                if n.right == n2:
                    #snode is in right subtree
                    #leave right subtree behind
                    n.right.parent = n.parent
                    if isLeft:
                        n.parent.left = n.right
                    else:
                        n.parent.right = n.right
                    
                    #move left subtree to the right
                    n.right = n.left
                    n.left = root_right
                else:
                    #snode is in left subtree
                    #leave left subtree behind
                    n.left.parent = n.parent
                    if isLeft:
                        n.parent.left = n.left
                    else:
                        n.parent.right = n.left
                    n.left = root_right
                    
                n.parent = self.root
                root_right.parent = n
                self.root.right = n

                #Inverse the OP
                inv_op =  inverse_op.get(n.op.type, False)
                if not inv_op:
                    raise SolverException(f"Could not find inverse operation for: {n.op.type}")
                n.op.type = inverse_op[n.op.type]
                n.op.value = self.inv_map[n.op.type]    
            
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
            return []
        return result
            
    def path(self, start_point):
        result = []
        curr = start_point
        while curr != None:
            result.append(curr)
            curr = curr.parent
        return result

if __name__ == "__main__":
    #s = Solver("(a+b-d)*c-7 = 1*4")
    s = Solver("(a+b-d)*c-7 = 1*4")
    r = s.solve("a")
    print(trace(r))