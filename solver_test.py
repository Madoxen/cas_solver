from solver import Solver


def test_dfs():
    s = Solver("a + b = a + c")
    res = s.dfs("a")
    assert len(res) == 2
