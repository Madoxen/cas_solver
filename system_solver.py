from collections import defaultdict
from copy import deepcopy
from typing import List
from attraction import attract
from equation_parser import AST, BinOp, Num, Parser, UnaryOp
from lexer import TokenType
from isolation import Solver, collect
from utils import create_graphviz_graph, inorder, trace


class SystemSolverException(Exception):
    pass

# represents a node of a tree


class SubstitutionTree:
    def __init__(self, eq, parent=None, children=[]) -> None:
        self.parent = parent
        self.equation = eq
        self.children: List[SubstitutionTree] = []
        # equations used in the past
        if parent != None:
            self.used_equations = deepcopy(parent.used_equations)
        else:
            self.used_equations = []

    def print_all(self):
        print(trace(self.equation))
        for c in self.children:
            c.print_all()

    def apply(self, func):
        """Apply function across whole tree"""
        func(self)
        for c in self.children:
            c.apply(func)


# Substitures var from eq with to
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
                    raise SystemSolverException(
                        "Equation tree in bad state - num node has a child.")


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
    """Gets solution without any unknowns"""
    # TODO: relax this method so that it returns solution with least
    # amount of unknowns
    if isSolution(sub_tree.equation):
        return sub_tree.equation
    for c in sub_tree.children:
        if isSolution(c.equation):
            return c.equation
        else:
            child_sol = getSolution(c)
            if child_sol != None and isSolution(child_sol):
                return child_sol
    return None  # base case for no children and no solution in root


class SystemSolver:
    def __init__(self):
        self.equations = []
        # dict for storing symbol to equation mapping
        # which we use to store information about which equation
        # contains what symbols
        self.symbol_eq_lookup = defaultdict(list)

    def extract_symbols(self, eq: BinOp) -> List[str]:
        """Returns list of existing symbols in the equation"""
        tree = inorder(eq)
        result = []
        for n in tree:
            if isinstance(n, Num):
                if n.token.type == TokenType.SYM:
                    result.append(n.value)
        return result

    def add_equation(self, eq: str):
        """Add equation to knowledge base"""
        self.equations.append(eq)
        r = Parser(eq).parse()
        tree = inorder(r)
        for n in tree:
            if isinstance(n, Num):
                if n.token.type == TokenType.SYM:
                    self.symbol_eq_lookup[n.value].append(eq)

    # solve for symbol
    def solve(self, target_symbol: str):
        # produce list of equations that contain target symbol
        target_symbol_equations = self.symbol_eq_lookup.get(
            target_symbol, None)
        if target_symbol_equations == None:
            raise SystemSolverException(
                "Could not find searched symbol in the knowledge base")

        # Try solving for every target equation
        for target_symbol_equation in target_symbol_equations:
            # Solve for searched symbol
            eq = Solver(target_symbol_equation).solve(target_symbol)
            root = SubstitutionTree(eq)
            root.used_equations.append(target_symbol_equation)
            symbols = self.extract_symbols(eq)
            symbols.remove(target_symbol)
            # go through every symbol other than searched symbol
            for s in symbols:
                # get equation that can be used to substitute symbols found in current equation
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
                    child.children.extend(
                        self.child_solve(child, target_symbol))
                    root.children.append(child)
        root.apply(lambda x: attract(x.equation))
        root.apply(lambda x: collect(x.equation))
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
                child.children.extend(self.child_solve(child, ssymbol))
                result.append(child)
        return result


s = SystemSolver()
# s.add_equation("x = y + z")
# s.add_equation("y + z = 2")
# r = s.solve("x")

# s.add_equation("x = z + y")
# s.add_equation("y = z")
# s.add_equation("y = v")
# s.add_equation("v = 2")
# r = s.solve("x")

# s.add_equation("ek = (m*v^2) / 2")
# s.add_equation("p = m*v")
# s.add_equation("p = 10")
# s.add_equation("m = 5")
# r = s.solve("ek")

# s.add_equation("r = 1/2 * a*t^2")
# s.add_equation("a = 10")
# s.add_equation("t = 20")
# r = s.solve("r")

s.add_equation("sin(x) = 2+z")
s.add_equation("z = sin(y)")
s.add_equation("y = 1")
r = s.solve("x")
sol = getSolution(r)

if sol != None:
    print(trace(sol))
else:
    print("No solution found.")
