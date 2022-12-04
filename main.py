import sys
from solver import Solver
from lexer import Lexer
from utils import trace


class CLIException(Exception):
    pass


if __name__ == "__main__":
    if len(sys.argv) < 3:
        # TODO: add more descriptive messages
        raise CLIException("Provide more arguments")

    equation_string = sys.argv[1]
    solve_for = sys.argv[2]

    s = Solver(equation_string)
    r = s.solve(solve_for)
    print(trace(r))
