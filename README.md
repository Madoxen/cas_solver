# cas_solver
Custom computer algebra system (CAS), done without using sympy.

## Goal
Consider the following equation: `x+1*5-2 = 1-x`, wouldn't it be nice to have computer perform necessary steps to calculate such equation?
Normal calculator won't do much here, they cannot _solve_ any equations; with help come [Computer Algebra Systems](https://en.wikipedia.org/wiki/Computer_algebra_system) (shorthand: CAS)
, think something in lines of very primitive [mathematica](https://www.wolfram.com/mathematica/). 

The goal of this project is to produce a simple CAS, solver will not evaluate integrals or solve differential equations, but most of high-school
maths will be supported. Things like basic algebra, trigonometry or exponentials.

## Principles of operation

Project consists of the following modules:
- Lexer - Converts user provided string into sequence of tokens
- Parser - Converts sequence of tokens into Abstract Syntax Tree (AST)
- Attraction - Attracts two, same symbols together, so that Collection can operate
- Collection - Joins two symbols / numbers together to reduce amount of symbols in the equation
- Isolation - Isolates searched unknown from the rest of the equation, following the rules of algebra

### Lexer

Lexer converts an equation string into a sequence of tokens. 

For example: `x+1*5-sin(2) = 1` will be converted into: `[SYM, BINOP, NUM, BINOP, NUM, BINOP, SYM, LPAR, NUM, RPAR, BINOP, NUM]`

We will also store values that were found in the equation: `[x, +, 1, *, 5, -, sin, (, 2, ), =, 1]`

That's it for the lexer!

We then can use the sequence to produce AST that encodes logical "flow" of an equation...

### Parser

Parser converts sequence of tokens into Abstract Syntax Tree, which encodes the relationships
between operations and operands, order of evaluation and automatically handles nested expressions. Below
you can find an example AST of the following equation: `sin(x+2+y+x) = 1`.

![miau](eq1.png "AST of sin(x+2+y+x) = 1")

Each token or group of tokens is converted into a tree's node. In our case we have the following types:
- `BinOp` - Shorthand for binary operation, an operation that takes two operands, the usual +, -, *, / etc.
- `UnaryOp` - Shorthand for unary operation, an operation that takes one operand, think functions like sin(x) or simple - operator (like -1)
- `Num` - Numbers and standalone symbols


## Running the project
To run the project simply clone it and then run: `python3 main.py "your_equation" symbol_to_solve_for`

NOTE: not everything is supported, in fact a very fraction of math is supported 
