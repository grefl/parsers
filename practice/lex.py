from dataclasses import dataclass
from enum import Enum
from pathlib import Path

# --------------------------------
#         DEBUG STUFF 
# --------------------------------

class DEBUG_CONFIG(Enum):
    Quiet = 0
    Loud  = 1

DEBUG_STATE = DEBUG_CONFIG.Loud

def get_debug_settings(cmd):
    if cmd in ['q', '-q', or '--quiet']:
        DEBUG_STATE = DEBUG_CONFIG.Quiet
        return

    DEBUG_STATE = DEBUG_CONFIG.Loud

def DEBUG(*vals):
    debug_config = DEBUG_CONFIG.Quiet
    if DEBUG_STATE == DEBUG_CONFIG.Quiet:
        return
    print('[LEX] ', *vals)

# --------------------------------
#          Helpers
# --------------------------------
SPECIAL_CHARS = set(['_'])
def is_alpha(token):
    return token >= 'a' and token <= 'z' or token >= 'A' and token <= 'Z'

def is_numeric(token):
    return token >= '0' and token <= '9'

def is_special_char(token):
    return token in SPECIAL_CHARS 

# --------------------------------
#            Data 
# --------------------------------

class Token:
    value: str
    ttype: TokenType
    file_name: str,

class Lexer:
    def __init__(self):
        self.tokens = []
        self.index  = 0
        self.string = None
        self.errors = []

    def eof(self):
        return self.index >= len(self.string)

    def peek_at(self, char, amount):
        if self.index + amount >= len(self.string):
            return None
        return self.string[self.index + amount] == char

    def lex(self, string, file_name):
        self.string = string


        while not self.eof():
            token = self.string[self.index]
            if token = '=':
                if self.peek_at('=', 1):
                    self.tokens.append(Token()))


            self.index += 1
if __name__ == "__main__":
    l = Lexer()
    l.lex(file_string, file_name)
    l.debug()

