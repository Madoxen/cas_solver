from parser import AST, UnaryOp
from solver import Solver
from lexer import TokenType
from utils import trace

#TODO: refactor test and code to not depend on 
#previous lexer and parser modules so that
#test failures wont cascade throught the code tree
#Make solver methods accept the parsed tree from outside

def test_dfs():
    s = Solver("a + b = a + c")
    res = s.dfs("a")
    assert len(res) == 2


def test_solver_add_left():
    #     =               =                                   
    #    / \             / \                    
    #   +   c    --->   a   -                    
    #  / \                 / \                   
    # a   b               c   b                            
    s = Solver("a+b=c")
    r = s.solve("a")
    
    assert r.op.type == TokenType.EQ 
    assert r.left.token.type == TokenType.SYM
    assert r.right.op.type == TokenType.MINUS
    assert r.right.left.token.type == TokenType.SYM
    assert r.right.right.token.type == TokenType.SYM
    assert r.right.left.value == "c"
    assert r.right.right.value == "b"


def test_solver_add_right():
    #     =               =                                   
    #    / \             / \                    
    #   +   c    --->   b   -                    
    #  / \                 / \                   
    # a   b               c   a                            
    s = Solver("a+b=c")
    r = s.solve("b")
    
    assert r.op.type == TokenType.EQ 
    assert r.left.token.type == TokenType.SYM
    assert r.left.value == "b"
    assert r.right.op.type == TokenType.MINUS
    assert r.right.left.token.type == TokenType.SYM
    assert r.right.right.token.type == TokenType.SYM
    assert r.right.left.value == "c"
    assert r.right.right.value == "a"
    

    
def test_solver_sub_left():
    #     =               =                                   
    #    / \             / \                    
    #   -   c    --->   a   +                    
    #  / \                 / \                   
    # a   b               c   b                            
    s = Solver("a-b=c")
    r = s.solve("a")
    
    assert r.op.type == TokenType.EQ 
    assert r.left.token.type == TokenType.SYM
    assert r.right.op.type == TokenType.PLUS
    assert r.right.left.token.type == TokenType.SYM
    assert r.right.right.token.type == TokenType.SYM
    assert r.right.left.value == "c"
    assert r.right.right.value == "b"


def test_solver_sub_right():
    # a - b = c  --->  b = -c + a 
    #     =               =                                   
    #    / \             / \                    
    #   -   c    --->   b   +                    
    #  / \                 / \                   
    # a  b                -   a
    #                    /
    #                   c                              
    s = Solver("a-b=c")
    r = s.solve("b")
    
    assert r.op.type == TokenType.EQ 
    assert r.left.token.type == TokenType.SYM
    assert r.left.value == "b"
    assert r.right.op.type == TokenType.PLUS
    assert isinstance(r.right.left, UnaryOp)
    assert r.right.left.token.type == TokenType.MINUS
    assert r.right.right.token.type == TokenType.SYM
    assert r.right.left.token.value == "-"
    assert r.right.right.value == "a"
    assert r.right.left.expr.token.type == TokenType.SYM
    assert r.right.left.expr.token.value == "c"
    


def test_solver_solve_mul_left():
    # a * b = c  ---> a = c / b  
    #     =               =                                   
    #    / \             / \                    
    #  *  c    --->     a  div                    
    #  / \                 / \                   
    # a   b               c   b                            

    
    s = Solver("a * b = c")
    r = s.solve("a")

    assert r.op.type == TokenType.EQ 
    assert r.left.token.type == TokenType.SYM
    assert r.right.op.type == TokenType.DIV
    assert r.right.left.token.type == TokenType.SYM
    assert r.right.right.token.type == TokenType.SYM
    assert r.right.left.value == "c"
    assert r.right.right.value == "b"

def test_solver_solve_mul_right():
    # a * b = c ---> b = c / a
    #     =               =                                   
    #    / \             / \                    
    #   *  c    --->   b   div                   
    #  / \                 / \                   
    # a   b               c   a                            

    #arrange
    s = Solver("a * b = c")

    #act
    r = s.solve("b")

    #assert 
    assert r.op.type == TokenType.EQ 
    assert r.left.token.type == TokenType.SYM
    assert r.left.token.value == "b"
    assert r.right.op.type == TokenType.DIV
    assert r.right.left.token.type == TokenType.SYM
    assert r.right.right.token.type == TokenType.SYM
    assert r.right.left.value == "c"
    assert r.right.right.value == "a"



def test_solver_solve_div_left():
    # a / b = c  ---> a = c * b  
    #     =               =                                   
    #    / \             / \                    
    #  div  c    --->   a   *                    
    #  / \                 / \                   
    # a   b               c   b                            

    
    s = Solver("a / b = c")
    r = s.solve("a")
    assert r.op.type == TokenType.EQ 
    assert r.left.token.type == TokenType.SYM
    assert r.right.op.type == TokenType.MUL
    assert r.right.left.token.type == TokenType.SYM
    assert r.right.right.token.type == TokenType.SYM
    assert r.right.left.value == "c"
    assert r.right.right.value == "b"

def test_solver_solve_div_right():
    # a / b = c ---> b = a / c
    #     =               =                                   
    #    / \             / \                    
    #  div  c    --->   b  div                    
    #  / \                 / \                   
    # a   b               a   c                            

    
    s = Solver("a / b = c")
    r = s.solve("b")
    assert r.op.type == TokenType.EQ 
    assert r.left.token.type == TokenType.SYM
    assert r.left.token.value == "b"
    assert r.right.op.type == TokenType.DIV
    assert r.right.left.token.type == TokenType.SYM
    assert r.right.right.token.type == TokenType.SYM
    assert r.right.left.value == "a"
    assert r.right.right.value == "c"



def test_solver_complex_eq():
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
