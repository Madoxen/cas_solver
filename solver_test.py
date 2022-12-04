from parser import UnaryOp
from solver import Solver
from lexer import TokenType

#TODO: refactor test and code to not depend on 
#previous lexer and parser modules so that
#test failures wont cascade throught the code tree
#Make solver methods accept the parsed tree from outside

def test_dfs():
    s = Solver("a + b = a + c")
    res = s.dfs("a")
    assert len(res) == 2


def test_solver_simpler():
    #     =               =                                   
    #    / \             / \                    
    #   +   c    --->   a   -                    
    #  / \                 / \                   
    # a   b               c   b                            
    s = Solver("a+b=c")
    r = s.solve("a")
    assert (
        r.op.type == TokenType.EQ 
        and r.left.token.type == TokenType.SYM
        and r.right.op.type == TokenType.MINUS
        and r.right.left.token.type == TokenType.SYM
        and r.right.right.token.type == TokenType.SYM
        and r.right.left.value == "c"
        and r.right.right.value == "b"
    )


def test_solver_simple():
    #             =               =                                   
    #            / \             / \                    
    #           -   1   --->    a   -                    
    #          / \                 / \                   
    #         *   7              div   b                      
    #        / \                 / \            
    #       +   c               +   c        
    #      / \                 / \
    #     a   b               1   7       
    s = Solver("(a+b)*c-7 = 1")
    
    r = s.solve("a")
    assert r.op.type == TokenType.EQ
    assert r.left.token.type == TokenType.SYM
    assert r.left.value == "a"
    assert r.right.op.type == TokenType.MINUS
    assert r.right.right.token.type == TokenType.SYM
    assert r.right.right.value == "b"
    assert r.right.left.op.type == TokenType.DIV
    assert r.right.left.right.value == "c"
    assert r.right.left.left.op.type == TokenType.PLUS
    assert r.right.left.left.left.value == 1
    assert r.right.left.left.right.value == 7
    
    s = Solver("(a+b)*c-7 = 1")
    r = s.solve("b")
    assert r.op.type == TokenType.EQ
    assert r.left.token.type == TokenType.SYM
    assert r.left.value == "b"
    assert r.right.op.type == TokenType.MINUS
    assert r.right.right.token.type == TokenType.SYM
    assert r.right.right.value == "a"
    assert r.right.left.op.type == TokenType.DIV
    assert r.right.left.right.value == "c"
    assert r.right.left.left.op.type == TokenType.PLUS
    assert r.right.left.left.left.value == 1
    assert r.right.left.left.right.value == 7


def test_solver_unary_op():
    # a / -c = b ---> c = -a/b
    #     =               =                                   
    #    / \             / \                    
    #  div   b    --->  c   -                    
    #  / \                  /                 
    # a   -                /   
    #      \              / \
    #       c            a   b  
    s = Solver("a/-c = b")
    r = s.solve("c")

    assert r.op.type == TokenType.EQ 
    assert r.left.token.type == TokenType.SYM
    assert r.right.op.type == TokenType.MINUS
    assert isinstance(r.right, UnaryOp)
    assert r.right.expr.op.type == TokenType.DIV
    assert r.right.expr.left.token.type == TokenType.SYM
    assert r.right.expr.right.token.type == TokenType.SYM
    assert r.right.expr.left.value == "a"
    assert r.right.expr.right.value == "b"
    assert r.left.value == "c"
