from pattern_matcher import match
from equation_parser import Parser

def pattern_matcher_test():
    tree = Parser("x+2+x=1").parse()
    pattern = Parser("x=1").parse()
    assert True == match(tree, pattern) 
