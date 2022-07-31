#!/usr/bin/env python3
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from pprint import pprint, pformat
import unittest
from lexer import Lexer,Token, TokenType
# lambda x: x.type_ != TokenType.RightParen or x.type_ != TokenType.NewLine
def DEBUG(x): 
    if x.type_ == TokenType.NewLine or x.type_ == TokenType.RightParen:
        return False
    return True

class ParsedTokenType(Enum):
    H1 = 0
    H2 = 1 
    H3 = 2 
    H4 = 3 
    H5 = 4 
    H6 = 5 
    P  = 6
    A  = 7
    IMG = 8

    Blockquote = 9
    UL         = 10
    OL         = 10

@dataclass
class ParsedToken:
    type_: ParsedTokenType
    value: str 

class Parser:

    def __init__(self, tokens):
        self.tokens        = tokens
        self.len           = len(self.tokens) -1
        self.idx =         -1 
        self.intermediate  = []
        self.prev_token    = None
        self.current_token = None
        self.next_token    = None

    def peek_token(self):
        if self.idx + 1 >= self.len:
            return None
        return self.tokens[self.idx +1]
    def get_token(self):
        if self.idx + 1 >= self.len:
            self.current_token = None
            self.next_token    = None
            return None
        self.idx +=1
        self.prev_token = self.current_token
        self.current_token = self.tokens[self.idx]
        self.next_token = self.peek_token()
        return self.current_token
            
    def parse(self):
        while self.get_token() is not None: 
            if self.current_token.type_ == TokenType.Hash_Tag:
                print('h1')
                if self.prev_token is None or self.prev_token.type_ == TokenType.NewLine:
                    # This token is a header. Now time to find what type - h1 or h2, etc.
                    print('is none')
                    first_hash = self.current_token
                    h1s = self.parse_while(lambda x: x.type_ == TokenType.Hash_Tag)
                    print(h1s)
                    # header_text = self.parse_while(lambda x: x.type_ != TokenType.NewLine)
                    header_text = self.parse_inner_block()
                    if len(h1s) == 1:
                        print('here')
                        self.intermediate.append(ParsedToken(ParsedTokenType.H1, header_text))
            elif self.current_token.type_ == TokenType.Dash and (self.prev_token is None or self.prev_token.type_ == TokenType.NewLine):
                print('new line')
                list_items = []
                list_items.append(Token(None, TokenType.NewLine, '\n'))
                while self.current_token is not None and self.current_token.type_ == TokenType.Dash:
                    list_item = self.parse_inner_block()
                    for item in list_item:
                        list_items.append(item)
                    # FIXME
                    list_items.append(Token(None, TokenType.NewLine, '\n'))
                print('got this far')
                print(self.current_token)
                print(list_items)
                self.intermediate.append(ParsedToken(ParsedTokenType.UL, list_items))
            elif self.current_token.type_ == TokenType.BlockQuoteStart:
                symbol = self.current_token
                block_quote_text = self.parse_inner_block() 
                self.intermediate.append(ParsedToken(ParsedTokenType.Blockquote, block_quote_text))
            elif self.current_token.type_ == TokenType.NewLine:
                print('new line')
                continue
            else:
                inner_tokens = self.parse_inner_block()
                P = ParsedToken(ParsedTokenType.P, inner_tokens)
                self.intermediate.append(P)
        return self.intermediate
    def parse_inner_block(self):
        inner_tokens = []
        while self.current_token is not None and self.current_token.type_ != TokenType.NewLine:
            print('here')
            if self.current_token.type_ == TokenType.Shebang and self.next_token.type_ == TokenType.LeftBracket:
                print('attempt')
                _shebang = self.current_token
                maybe_image = self.parse_while(DEBUG)
                print('done')
                if self.current_token.type_ == TokenType.RightParen:
                    maybe_image.append(self.current_token)
                    inner_tokens.append(ParsedToken(ParsedTokenType.IMG, maybe_image))
                else:
                    inner_tokens.append(maybe_image)
            else:
                inner_tokens.append(self.current_token)
            self.get_token()
        if self.current_token is not None and self.current_token.type_ == TokenType.NewLine:
            self.get_token()
        return inner_tokens
    def parse_while(self, predicate):
        parsed_token = []
        while self.current_token is not None and predicate(self.current_token):
            if self.current_token.type_ == TokenType.RightParen:
                print('got it')
                print(self.current_token.type_ != TokenType.RightParen)
            print('why')
            parsed_token.append(self.current_token)
            self.get_token()
        return parsed_token

def main():
    file_string = Path('./list.md').read_text()

    p = Lexer(file_string)

    print("BEGIN LEX")
    tokens = p.lex()
    pprint(tokens)

    print("BEGIN PARSE")
    p = Parser(tokens)
    parsed_tokens = p.parse()
    formatted = pformat(parsed_tokens, width=1)
    Path('./debug_tokens').write_text(formatted)


if __name__ == "__main__":
    main()
