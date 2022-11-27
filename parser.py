from lexer import Lexer, TokenType
# nodes with no children are called leafs
# general parser structure inspired by: https://ruslanspivak.com/lsbasi-part7/
class AST:
    def __init__(self, parent):
        self.parent = parent

class BinOp(AST):
    def __init__(self, left: AST, op, right: AST, parent = None):
        super().__init__(parent)
        self.left = left
        self.token = self.op = op
        self.right = right
        self.left.parent = self
        self.right.parent = self

#Note: num can represent negative values as well
#Which in current version will lead to something like
# a - -b
#TODO: somehow handle this case 
class Num(AST):
    def __init__(self, token, parent = None):
        super().__init__(parent)
        self.token = token
        self.value = token.value

class ParserException(Exception):
    pass

#TODO: Add missing token implementation exceptions for missing token types
class Parser:
    def __init__(self, string):
        self.tokens = Lexer().lex(string)
        self.current_token = self.tokens[0]
        self.pos = 0
    
    def eat(self, type):
        if self.current_token.type == type:
            self.pos += 1
            self.current_token = self.tokens[self.pos]
        else:
            raise ParserException("Invalid syntax")

    def factor(self):
        """factor : TokenType.NUM | LPAREN expr RPAREN"""
        token = self.current_token
        if token.type == TokenType.NUM:
            self.eat(TokenType.NUM)
            return Num(token)
        if token.type == TokenType.SYM:
            self.eat(TokenType.SYM)
            return Num(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node

    def term(self): 
        """term : factor ((TokenType.MUL | TokenType.DIV) factor)*"""
        node = self.factor()

        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
            elif token.type == TokenType.DIV:
                self.eat(TokenType.DIV)

            node = BinOp(left=node, op=token, right=self.factor())

        return node

    def expr(self):
        """
        expr   : term ((TokenType.PLUS | TokenType.MINUS) term)*
        term   : factor ((TokenType.MUL | TokenType.DIV) factor)*
        factor : TokenType.NUM | LPAREN expr RPAREN
        """
        node = self.term()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            token = self.current_token
            if token.type == TokenType.PLUS:
                self.eat(TokenType.PLUS)
            elif token.type == TokenType.MINUS:
                self.eat(TokenType.MINUS)

            node = BinOp(left=node, op=token, right=self.term())
        return node

    def equation(self): 
        node = self.expr()
        while self.current_token.type == TokenType.EQ:
            token = self.current_token
            if token.type == TokenType.EQ:
                self.eat(TokenType.EQ)
            #Equation should be the root of the expression tree
            node = BinOp(left=node, op=token, right=self.expr(), parent=None)
        return node


    def parse(self):
        return self.equation()