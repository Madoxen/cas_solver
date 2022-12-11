from system_solver import SystemSolver


def test_simple():
    s = SystemSolver()
    s.add_equation("x = z + y")
    s.add_equation("y = z")
    s.add_equation("y = v")
    s.add_equation("v = 2")
    r = s.solve("x")

    