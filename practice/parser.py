from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from lex import TokenType, Lexer 

def DEBUG(*vals):
    print('[parser] ', *vals)



# ------------------------------
#           Helpers
# ------------------------------

# ------------------------------
#            Data
# ------------------------------

@dataclass
class Node:
    literal: str

@dataclass
class Statement:
    Node: Node

@dataclass
class Expression:
    Node: Node

@dataclass
class LetStatement:
    name: str
    value: Expression

@dataclass
class ReturnStatement:
    return_value: Expression

# ------------------------------
#           Parser 
# ------------------------------

class Parser:
    def __init__(self, tokens):
        self.tokens      = tokens
        self.statements  = []
        self.index       = 0
        self.next_index  = 0
        self.token       = None
        self.next_token  = None


    def peek_at(self, token_type, amount):
        if self.index + amount >= len(self.tokens):
            return None
        return token_type == self.tokens[self.index + amount].ttype
    
    def next(self):
        if self.index >= len(self.tokens):
            self.token = None
            return self.token

        self.token = self.next_token 
        self.index = self.next_index 
        self.next_index +=1
        if self.next_index >= len(self.tokens):
            self.next_token = None 
        else:
            self.next_token = self.tokens[self.next_index]

        return self.token 
    def expect_next(self, token_type):
        if self.peek_at(token_type, 1):
            self.next()
            return True

        return False

    def parse_let_statement(self):

        if not self.expect_next(TokenType.Literal):
            self.errors.append(f"missing literal after 'let' at index -> {self.index}")
            return None
        let_statement = LetStatement(self.token.value, None)

        if not self.expect_next(TokenType.Assign):
            self.errors.append(f"missing '=' after 'literal' at index -> {self.index}")
            return None

        while self.token.ttype != TokenType.Newline:
            self.next()

        return let_statement

    def parse_return_statement(self):

        return_statement = ReturnStatement(None)

        while self.token.ttype != TokenType.Newline:
            self.next()

        return return_statement



    def parse_statement(self):
        if self.token.ttype == TokenType.Keyword and self.token.value == 'let':
            return self.parse_let_statement()
        elif self.token.ttype == TokenType.Keyword and self.token.value == 'return':
            return self.parse_return_statement()
        return None
    def debug(self):
        for statement in self.statements:
            DEBUG(statement)

    def parse(self):
        self.next()
        self.next()
        while self.token is not None:
            statement = self.parse_statement()
            if statement:
                self.statements.append(statement)
            
            self.next()
        return self.statements


if __name__ == "__main__":
    file_name   = 'example.lang'
    file_string = Path(file_name).read_text()

    l = Lexer(file_string, file_name)
    l.lex()

    p = Parser(l.tokens)

    p.parse()
    p.debug()


