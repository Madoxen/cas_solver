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
    FUNC = 10
    EOF = 999


class Token: 
    def __init__(self, value, type):
        self.value = value
        self.type = type

class LexerException(Exception):
    pass        

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
        self.max_pos = 0

    def _next_char(self):
        self.current_pos += 1
        if self.current_pos < self.max_pos:
            self.current_char = self.string[self.current_pos]
        else: 
            self.current_char = "\0"

    def lex(self, string: str) -> List[Token]:
        result = []
        self.string = string
        self.max_pos = len(string)
        self.current_char = string[self.current_pos]
        while self.current_token.type != TokenType.EOF:
            self.current_token = self._get_next_token()
            result.append(self.current_token)
        return result

    #TODO: refactor, extract functions processing
    #different parts.
    #TODO: add more diagnostics, exceptions
    def _get_next_token(self) -> Token:
        #Skip spaces
        #TODO: support for other white spaces
        if self.current_char == ' ':
            while self.current_char == ' ':
                self._next_char()

        if self.current_pos >= len(self.string):
            return Token("\0", TokenType.EOF)

        #Number tokens
        if self.current_char.isdigit():
            #TODO: support for floats
            curr_char = self.current_char
            pos = self.current_pos
            tok = ""
            #Take contiguous string of numbers
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
        
        #Symbol and tokens
        if self.current_char.isalpha():
            curr_char = self.current_char
            pos = self.current_pos
            tok = ""
            #Take contiguous string of alphabetic characters (word)
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
        
        #1-char tokens/operators
        if len(self.current_char) == 1:
            op = self.operators.get(self.current_char, None)
            if op == None:
                raise LexerException(f"Invalid operator: {repr(self.current_char)}")
            char_op = self.current_char
            self._next_char() #Advance character pointer
            return Token(char_op, op)