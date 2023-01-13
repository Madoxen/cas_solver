from system_solver import SystemSolver, getSolution
from utils import trace


def test_simple():
    s = SystemSolver()
    s.add_equation("x = z + y")
    s.add_equation("y = z")
    s.add_equation("y = v")
    s.add_equation("v = 2")
    r = s.solve("x")
    assert trace(getSolution(r)) == "x=4"


def test_recursive():
    s = SystemSolver()
    s.add_equation("x = y + z")
    s.add_equation("y + z = 2")
    r = s.solve("x")
    assert trace(getSolution(r)) == "x=2"


def test_physics():
    s = SystemSolver()
    s.add_equation("ek = (m*v^2) / 2")
    s.add_equation("p = m*v")
    s.add_equation("p = 10")
    s.add_equation("m = 5")
    r = s.solve("ek")
    assert trace(getSolution(r)) == "ek=10.0"

def test_trig():
    s = SystemSolver()
    s.add_equation("sin(x) = 2+z")
    s.add_equation("z = sin(y)")
    s.add_equation("y = 1")
    r = s.solve("x")
    assert trace(getSolution(r)) == "x=asin((2+sin(1)))"
