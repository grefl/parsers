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
KEYWORDS = set(['let', 'const', 'def', 'in', 'for', 'none', 'false', 'true'])

def get_debug_settings(cmd):
    if cmd in ['q', '-q', '--quiet']:
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
def is_alphanumeric(token):
    return is_alpha(token) or is_numeric(token) or is_special_char(token)
def is_whitespace(token):
    return token == ' ' or token == '\t' or token == '\n'
# --------------------------------
#            Data 
# --------------------------------
class TokenType(Enum):
    Shebang      = "!"
    Assign       = "="
    Eql          = "=="
    Greater      = '>'
    GreaterEql   = '>='
    Less         = '<'
    LessEql      = '<='
    Newline      = 0
    Whitespace   = 1
    Unknown      = 2
    Keyword      = 3
    Literal      = 4
    Int          = 5
    Float        = 6 
    String       = 7
@dataclass
class Token:
    value: str
    ttype: TokenType
    file_name: str

class Lexer:
    def __init__(self, string, file_name):
        self.tokens = []
        self.index  = 0
        self.string = string
        self.file_name = file_name 
        self.errors = []

    def eof(self):
        return self.index >= len(self.string)

    def peek_at(self, char, amount):
        if self.index + amount >= len(self.string):
            return None
        return self.string[self.index + amount] == char

    # TODO:(greg) add float lexing next
    def try_lex_number(self):
        number = []
        while not self.eof() and is_numeric(c := self.string[self.index]):
                number.append(c)
                self.index +=1
        return ''.join(number)

    def try_parse_literal_or_keyword(self):
        literal = []
        while not self.eof() and is_alphanumeric(c := self.string[self.index]):
                literal.append(c)
                self.index +=1
        return ''.join(literal)
    def parse_string_or_error(self):
        string = []
        start_index = self.index
        self.index +=1
        while not self.eof() and (c := self.string[self.index]) != '"':
            string.append(c)
            self.index += 1
        if self.eof():
            self.errors.append("Couldn't pass string literal")
            return
        DEBUG(string)
        return ''.join(string)
    def lex(self):


        while not self.eof():
            token = self.string[self.index]
            if  is_whitespace(token):
                DEBUG("Skipping whitespace for now")
                self.index +=1
                continue
            elif token == '=':
                if self.peek_at('=', 1):
                    self.index +=1
                    token += self.string[self.index]
                    self.tokens.append(Token(token, TokenType.Eql, self.file_name))
                else:
                    self.tokens.append(Token(token, TokenType.Assign, self.file_name))
            elif token == '>':
                if self.peek_at('=', 1):
                    self.index +=1
                    token += self.string[self.index]
                    self.tokens.append(Token(token, TokenType.GreaterEql, self.file_name))
                else:
                    self.tokens.append(Token(token, TokenType.Greater, self.file_name))
            elif is_numeric(token):
                int_or_float = self.try_lex_number()
                if '.' in int_or_float:
                    self.tokens.append(Token(int_or_float, TokenType.Float, self.file_name))
                else:
                    self.tokens.append(Token(int_or_float, TokenType.Int, self.file_name))
            elif token == '"':
                parsed_string = self.parse_string_or_error()
                self.tokens.append(Token(parsed_string, TokenType.String, self.file_name))
            else:
                keyword_or_literal = self.try_parse_literal_or_keyword()
                if keyword_or_literal in KEYWORDS:
                    self.tokens.append(Token(keyword_or_literal, TokenType.Keyword, self.file_name))
                else:
                    self.tokens.append(Token(keyword_or_literal, TokenType.Literal, self.file_name))


            self.index += 1
    def debug(self):
        for token in self.tokens:
            DEBUG(token)
if __name__ == "__main__":
    file_name = 'example.lang'
    file_string = Path(file_name).read_text()
    l = Lexer(file_string, file_name)
    l.lex()
    l.debug()

