from lexer import Lexer, TokenType, Token
# nodes with no children are called leafs
class AST:
    def __init__(self, parent):
        self.parent = parent

    def isLeft(self) -> bool:
        """Returns True if instance of the class is the left node of a parent
        else False."""
        if isinstance(self.parent, BinOp):
            return self == self.parent.left
        return False

class BinOp(AST):
    def __init__(self, left: AST, op: Token, right: AST, parent = None):
        super().__init__(parent)
        self.left = left
        self.token = self.op = op
        self.right = right
        self.left.parent = self
        self.right.parent = self

class UnaryOp(AST):
    def __init__(self, expr: AST, op: Token, parent = None):
        super().__init__(parent)
        self.expr = expr
        self.token = self.op = op
        self.expr.parent = self

class Num(AST):
    def __init__(self, token: Token, parent = None):
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
        """factor : (PLUS | MINUS) factor | INTEGER | SYMBOL | LPAREN expr RPAREN"""
        token = self.current_token
        if token.type == TokenType.PLUS:
            self.eat(TokenType.PLUS)
            node = UnaryOp(self.factor(), token)
            return node
        elif token.type == TokenType.MINUS:
            self.eat(TokenType.MINUS)
            node = UnaryOp(self.factor(), token)
            return node
        elif token.type == TokenType.SYM:
            self.eat(TokenType.SYM)
            if self.current_token.type == TokenType.LPAREN:
                self.eat(TokenType.LPAREN)
                node = UnaryOp(self.expr(), Token(token.value, TokenType.FUNC))
                self.eat(TokenType.RPAREN)
                return node
            else:
                return Num(token)
        elif token.type == TokenType.NUM:
            self.eat(TokenType.NUM)
            return Num(token)
        elif token.type == TokenType.LPAREN:
            self.eat(TokenType.LPAREN)
            node = self.expr()
            self.eat(TokenType.RPAREN)
            return node
        #TODO: more descriptive error message 
        #raise ParserException("Bad syntax")

    def powers(self): 
        node = self.factor()

        while self.current_token.type == TokenType.POW:
            token = self.current_token
            if token.type == TokenType.POW:
                self.eat(TokenType.POW)
            
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def term(self): 
        """term : factor ((TokenType.MUL | TokenType.DIV) factor)*"""
        node = self.powers()

        while self.current_token.type in (TokenType.MUL, TokenType.DIV):
            token = self.current_token
            if token.type == TokenType.MUL:
                self.eat(TokenType.MUL)
            elif token.type == TokenType.DIV:
                self.eat(TokenType.DIV)

            node = BinOp(left=node, op=token, right=self.powers())

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


    #Lowest priority
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

def parse(string: str):
    return Parser(string).parse()


parse("x=sin(1+2)")