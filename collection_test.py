from collection import collect
from equation_parser import parse
from utils import trace


def test_collect_mul_pow():
    r = parse("x^2*x^3=1")
    collect(r)
    assert trace(r) == "(x^5)=1"



def test_collect_div_pow():
    r = parse("x^2/x^3=1")
    collect(r)
    assert trace(r) == "(x^-1)=1"