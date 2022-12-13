from system_solver import SystemSolver, getSolution
from utils import trace


def test_simple():
    s = SystemSolver()
    s.add_equation("x = z + y")
    s.add_equation("y = z")
    s.add_equation("y = v")
    s.add_equation("v = 2")
    r = s.solve("x")
    assert trace(getSolution(r)) == "x=(2+2)"

