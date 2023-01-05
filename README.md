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




## Running the project
To run the project simply clone it and then run: `python3 main.py "your_equation" symbol_to_solve_for`
