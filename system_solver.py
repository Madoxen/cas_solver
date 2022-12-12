from collections import defaultdict
from copy import deepcopy
from typing import List
from equation_parser import AST, BinOp, Num, Parser, UnaryOp
from lexer import TokenType
from solver import Solver
from utils import inorder, trace

class SystemSolverException(Exception):
    pass

#represents a node of a tree
class SubstitutionTree: 
    def __init__(self, eq, parent = None, children = []) -> None:
        self.parent = parent
        self.equation = eq
        self.children : List[SubstitutionTree] = []
        #equations used in the past
        if parent != None:
            self.used_equations = deepcopy(parent.used_equations)
        else:
            self.used_equations = []

    def print_all(self):
        print(trace(self.equation))
        for c in self.children:
            c.print_all()



#Substitures var from eq with to 
#TODO: test the method
def substitute(eq: BinOp, var: str, to: AST):
    nodes = inorder(eq)
    for n in nodes:
        if isinstance(n, Num):
            if n.token.type == TokenType.SYM and n.value == var:
                if isinstance(n.parent, BinOp):
                    if n.isLeft():
                        n.parent.left = to
                    else:
                        n.parent.right = to
                    to.parent = n.parent
                elif isinstance(n.parent, UnaryOp):
                    n.parent.expr = to
                    to.parent = n.parent
                else: 
                    raise SystemSolverException("Equation tree in bad state - num node has a child.")
                    

def isSolution(eq: BinOp) -> bool:
    """Checks if provided equation is a solution

        For equation to be a solution, the right
        side of the equation shall contain no SYM tokens
    """
    
    eqright = inorder(eq.right)
    for n in eqright:
        if isinstance(n, Num) and n.token.type == TokenType.SYM:
            return False
    return True
    

def getSolution(sub_tree: SubstitutionTree):
    if isSolution(sub_tree.equation):
        return sub_tree.equation
    for c in sub_tree.children:    
        if isSolution(c.equation):
            return c.equation
        else:
            child_sol = getSolution(c)
            if child_sol != None and isSolution(child_sol):
                return child_sol
    return None #base case for no children and no solution in root
 

class SystemSolver:
    def __init__(self):
        self.equations = []
        #dict for storing symbol to equation mapping
        #which we use to store information about which equation
        #contains what symbols
        self.symbol_eq_lookup = defaultdict(list)
   

    def extract_symbols(self, eq: BinOp) -> List[str]:
        tree = inorder(eq)
        result = []
        for n in tree:
            if isinstance(n, Num):
                if n.token.type == TokenType.SYM:
                    result.append(n.value)
        return result


    def add_equation(self, eq: str):
        self.equations.append(eq)
        r = Parser(eq).parse()
        tree = inorder(r)
        for n in tree:
            if isinstance(n, Num):
                if n.token.type == TokenType.SYM:
                    self.symbol_eq_lookup[n.value].append(eq)
        

    #solve for symbol
    def solve(self, ssymbol: str):
        """Symbolicaly solving system of equations is a search problem ?

            Solving system of equations is the same as solving a search problem
            ""Find a set of substitutions such that the resulting equation will
            contain only known values

            Example:
            Solve for x:
            x = y + z * 2
            y = 2
            z = e
            e = 1

                Available substitutions for equation 1.
                y = 2
                z = e

                Apply substitutions:
                x = 2 + e * 2

                Available substitutions for current equation: 
                e = 1

                Apply substitutions:
                x = 2 + 1 * 2 

            End.

            This was somewhat trivial example. Sometimes we can make a 
            wrong substitution:

            x = y + z * 2
            y = 2
            z = f
            z = e
            e = 1

                Available substitutions for equation 1.
                y = 2
                z = f

                Apply substitutions:
                x = 2 + f * 2

                Available substitutions for current equation: 
                None

                Backtrack and choose different option:
                x = y + z * 2

                Available substitutions for equation 1.
                y = 2
                z = e                

                Apply substitutions:
                x = 2 + e * 2 

                Available substitutions for current equation: 
                e = 1

                Apply substitutions:
                x = 2 + 1 * 2 

                End.
                
                A certain structure emerges - a tree of substitutions.

                We can represent the above process with a tree
                                      1
                                 /    |    \
                                2     3     4
                               / \   / \   / \
                              3   4 2   5 5   2
                                  |       |
                                  5       2
                
        """
        ssymbol_equations = self.symbol_eq_lookup.get(ssymbol, None)
        if ssymbol_equations == None:
            raise SystemSolverException("Could not find searched symbol")
        
        for ss_eq in ssymbol_equations: 
            #Transform equation so that only searched symbol remains on the left side
            eq = Solver(ss_eq).solve(ssymbol)
            root = SubstitutionTree(eq)
            root.used_equations.append(ss_eq)
            symbols = self.extract_symbols(eq)
            symbols.remove(ssymbol)
            #go through every symbol other than searched symbol
            for s in symbols:
                for sub_eq in self.symbol_eq_lookup[s]:
                    if sub_eq in root.used_equations:
                        continue
                    cheq = deepcopy(eq)
                    solver = Solver(sub_eq)
                    sub = solver.solve(s)
                    sub = sub.right
                    substitute(cheq, s, sub)
                    child = SubstitutionTree(cheq, root)
                    child.used_equations.append(sub_eq)
                    child.children.extend(self.child_solve(child, ssymbol))
                    root.children.append(child)
        return root

    
    def child_solve(self, node: SubstitutionTree, ssymbol: str) -> List[SubstitutionTree]:
        eq = node.equation
        symbols = []
        result = []
        symbols = self.extract_symbols(eq)
        try:
            symbols.remove(ssymbol)
        except:
            pass
        for s in symbols:
                for sub_eq in self.symbol_eq_lookup[s]:
                    if sub_eq in node.used_equations:
                        continue
                    cheq = deepcopy(eq)
                    solver = Solver(sub_eq)
                    sub = solver.solve(s)
                    sub = sub.right
                    substitute(cheq, s, sub)
                    child = SubstitutionTree(cheq, node)
                    child.used_equations.append(sub_eq)
                    child.children.extend(self.child_solve(child,ssymbol))
                    result.append(child)
        return result

s = SystemSolver()
# s.add_equation("x = z + y")
# s.add_equation("y = z")
# s.add_equation("z = f")
# s.add_equation("y = v")
# s.add_equation("v = 2")

# s.add_equation("x = y + z")
# s.add_equation("y + z = 2")
# r = s.solve("x")
s.add_equation("ek = (m*v^2) / 2")
s.add_equation("p = m*v")
s.add_equation("p = 10")
s.add_equation("m = 5")

r = s.solve("v")
r.print_all()
print(trace(getSolution(r)))