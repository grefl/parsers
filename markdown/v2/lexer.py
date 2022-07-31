#!/usr/bin/env python3
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from pprint import pprint
import unittest

class TokenType(Enum):
    Hash_Tag          = '#'
    Asterix           = '*' 
    UnderScore        = '_'
    Dash              = '-'
    LeftBracket       = '['
    RightBracket      = ']'
    LeftParen         = '('
    RightParen        = ')'
    BlockQuoteStart   = '>'
    Shebang           = '!'
    Tilda             = '`'
    Ordered_List_Item = 0
    Text              = 1
    NewLine           = 2
    WhiteSpace        = 3
    Unknown           = 4 

@dataclass
class Token:
    file_name: str
    type_: TokenType
    value: str



def is_whitespace(token):
    return token == ' ' or token == '\n' or token == '\t'

def is_alpha(token):
    return token >= 'a' and token <= 'z' or token >= 'A' and token <= 'Z'

def is_numeric(token):
    return token >= '1' and token <= '9'

def is_alphanumeric(token):
    return is_alpha(token) or is_numeric(token)

class Lexer:
    def __init__(self, string):
        self.tokens        = []
        self.idx           = 0
        self.current_token = None
        self.string = string
        self.len = len(self.string)-1

    def peek(self):
        if self.idx + 1 >= self.len:
            return None
        return self.string[self.idx + 1]

    def lex(self):

        while self.idx <= self.len:
            token = self.string[self.idx]
            if token == '#':
                self.tokens.append(Token(None, TokenType.Hash_Tag, token))
            elif token == '*':
                self.tokens.append(Token(None, TokenType.Asterix, token))
            elif token == '_':
                self.tokens.append(Token(None, TokenType.UnderScore, token))
            elif token == '-':
                self.tokens.append(Token(None, TokenType.Dash, token))
            elif token == '[':
                self.tokens.append(Token(None, TokenType.LeftBracket, token))
            elif token == ']':
                self.tokens.append(Token(None, TokenType.RightBracket, token))
            elif token == '(':
                self.tokens.append(Token(None, TokenType.LeftParen, token))
            elif token == ')':
                self.tokens.append(Token(None, TokenType.RightParen, token))
            elif token == '>':
                self.tokens.append(Token(None, TokenType.BlockQuoteStart, token))
            elif token == '!':
                self.tokens.append(Token(None, TokenType.Shebang, token))
            elif token == '~':
                self.tokens.append(Token(None, TokenType.Tilda, token))
            elif is_whitespace(token):
                if token == '\n':
                    self.tokens.append(Token(None, TokenType.NewLine, token))
                else:
                    self.tokens.append(Token(None, TokenType.WhiteSpace, token))
            elif is_alphanumeric(token):
                lexed_token = self.try_to_lex_text(token)
                self.tokens.append(Token(None, TokenType.Text, lexed_token))
                continue
            else:
                self.tokens.append(Token(None, TokenType.Unknown, token))
            self.idx +=1

        return self.tokens

    def try_to_lex_text(self, token):
        lexed_token = []

        while self.idx <= self.len and is_alphanumeric(self.string[self.idx]):
            token = self.string[self.idx]
            lexed_token.append(token) 
            self.idx +=1
        return ''.join(lexed_token)

def unwind_tokens(tokens):
    """
    This function unwinds the tokens given to it and instead returns the values as a string.

    Example: 

    ==========================================================================================
    input  = [Token(None, TokenType.Hash_Tag, '#'), Token(None, TokenType.RightParen, ')')]
    output = unwind_tokens(input)
    print(output) -> '#)' 
    ==========================================================================================
    """
    return ''.join([token.value for token in tokens])

def unwind_tokens_with_type(tokens):
    """
    This function unwinds the tokens given to it and instead returns an
    array of tuples with the first value as the TokenType and the second 
    as the literal value.

    Example: 

    ==========================================================================================
    input  = [Token(None, TokenType.Hash_Tag, '#'), Token(None, TokenType.RightParen, ')')]
    output = unwind_tokens(input)
    print(output) -> [(TokenType.Hash_Tag, '#'), (TokenType.RightParen, ')')] 
    ==========================================================================================
    """
    return [(token.type_, token.value) for token in tokens]

class Test(unittest.TestCase):

    def test_1(self):
        input_string = '#*_-[]'
        expected = '#*_-[]'

        p = Lexer(input_string)
        tokens = p.lex()
        actual = unwind_tokens(tokens) 

        self.assertEqual(expected, actual)

    def test_2(self):
        input_string = '#*'
        expected = [(TokenType.Hash_Tag, '#'), (TokenType.Asterix, '*')]

        p = Lexer(input_string)
        tokens = p.lex()
        actual = unwind_tokens_with_type(tokens) 
        
        self.assertEqual(expected, actual)

    def test_3(self):
        input_string = '[name](url)' 
        expected = input_string 

        p = Lexer(input_string)
        tokens = p.lex()
        actual = unwind_tokens(tokens) 

        self.assertEqual(expected, actual)

def main():

    file_string = Path('./alacritty.md').read_text()

    p = Lexer(file_string)

    tokens = p.lex()

    pprint(tokens)

if __name__ == "__main__":
    unittest.main()
    # main()

        
