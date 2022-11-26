from enum import Enum
from typing import List


class TokenType(Enum):
    BEGIN = -1
    PLUS = 0
    MINUS = 1
    MUL = 2
    DIV = 3
    POW = 4
    NUM = 5
    SYM = 6
    EQ = 7
    LPAREN = 8
    RPAREN = 9
    EOF = 999


class Token: 
    def __init__(self, value, type):
        self.value = value
        self.type = type

class Lexer:
    """Converts string input into tokens
    
    - Consecutive numbers like 3, 2313 or 3.14 are converted into NUM
    - Symbols -, +, *, /, ^ are converted, respectively, into MINUS, PLUS, MUL, DIV, POW
    - Parenthesis (, ) are converted, respectively, into LPAREN, RPAREN
    - Words: a, ab, haha are converted into SYM
    - TODO: Functions: a(...) are converted into FUNC 
    """

    operators = {
        '+' : TokenType.PLUS,
        '-' : TokenType.MINUS,
        '*' : TokenType.MUL,
        '/' : TokenType.DIV,
        '^' : TokenType.POW,
        '=' : TokenType.EQ,
        '(' : TokenType.LPAREN,
        ')' : TokenType.RPAREN
    }

    def __init__(self):
        self.current_char = None
        self.current_token = Token("",TokenType.BEGIN)
        self.current_pos = 0
        self.string = ""

    def lex(self, string: str) -> List[Token]:
        result = []
        self.string = string
        self.current_char = string[self.current_pos]
        while self.current_token.type != TokenType.EOF:
            self.current_token = self._get_next_token()
            result.append(self.current_token)
        return result

    def _get_next_token(self) -> Token:
        if self.current_pos >= len(self.string):
            return Token("\0", TokenType.EOF)

        if self.current_char == ' ':
            while self.current_char == ' ':
                self.current_pos += 1
                print(self.current_char)
                self.current_char = self.string[self.current_pos]

        if self.current_char.isdigit():
            #todo: support for floats
            curr_char = self.current_char
            pos = self.current_pos
            tok = ""
            while curr_char.isdigit():
                tok += curr_char
                pos += 1
                if pos < len(self.string):
                    curr_char = self.string[pos]
                else:
                    break
            self.current_pos = pos
            self.current_char = curr_char
            return Token(int(tok), TokenType.NUM)
        
        if self.current_char.isalpha():
            #todo: support for floats
            curr_char = self.current_char
            pos = self.current_pos
            tok = ""
            while curr_char.isalpha():
                tok += curr_char
                pos += 1
                if pos < len(self.string):
                    curr_char = self.string[pos]
                else:
                    break
            self.current_pos = pos
            self.current_char = curr_char
            return Token(tok, TokenType.SYM)
        
        if len(self.current_char) == 1:
            op = self.operators.get(self.current_char, None)
            if op == None:
                raise Exception("Invalid operator")
            char_op = self.current_char
            self.current_pos += 1
            self.current_char = self.string[self.current_pos]
            return Token(char_op, op)
    


def test_lexer_simple_num():
    l = Lexer()
    r = l.lex("1")
    assert r[0].type == TokenType.NUM and r[0].value == 1
    l = Lexer()
    r = l.lex("12")
    assert r[0].type == TokenType.NUM and r[0].value == 12

def test_lexer_simple_sym():
    l = Lexer()
    r = l.lex("a")
    assert r[0].type == TokenType.SYM and r[0].value == "a"
    l = Lexer()
    r = l.lex("ab")
    assert r[0].type == TokenType.SYM and r[0].value == "ab"

def test_lexer_expression():
    input = "a + b"
    l = Lexer()
    r = l.lex(input)
    print(r[0].value)
    print(r[1].value)
    assert r[0].type == TokenType.SYM and r[1].type == TokenType.PLUS and r[2].type == TokenType.SYM and r[3].type == TokenType.EOF