from pathlib import Path
from parser import Parser, ParsedTokenType
from lexer import Lexer, TokenType
def DEBUG(*vals): 
    formatted = " ".join([str(v) for v in vals])
    print(f"[DEBUG]: {formatted}")

def is_block_element(token_type):
    return token_type == ParsedTokenType.IMG or token_type == ParsedTokenType.H1 or token_type == ParsedTokenType.P or token_type == ParsedTokenType.UL

def unwind_image(values):
    output = []
    output.append('<img ')
    index = 0
    while index < len(values):
        val = values[index]
        if val.type_ == TokenType.Shebang:
            index +=2
            val = values[index]
            output.append(f'alt="{val.value}"')

        elif val.type_ == TokenType.LeftParen:
            index +=1
            url = values[index] 
            output.append(f'src="{url.value}"')
        index +=1
    output.append('/>')
    return ''.join(output)
class ReadTokensToWriteIntoHtml:
    def __init__(self, parsed_tokens):
        self.parsed_tokens = parsed_tokens

    def debug(self):
        html = []
        for parsed_token in parsed_tokens:
            DEBUG(parsed_token.type_)
            DEBUG(parsed_token.value)
            html.append(self.recurse(parsed_token))
        DEBUG("HTML")
        DEBUG('\n'.join(html))
    def recurse(self, token):
        output = []
        DEBUG("BEGIN RECURSIVE")
        DEBUG(token)
        if not is_block_element(token.type_):
            return token.value
        if token.type_ == ParsedTokenType.IMG:
           IMG = unwind_image(token.value) 
           return IMG
        for val in token.value:
            inner = self.recurse(val)
            output.append(inner)
        return ''.join(output)

        

if __name__ == "__main__":

    file_string = Path('./tiny.md').read_text()

    l = Lexer(file_string)
    tokens = l.lex()

    p = Parser(tokens)
    parsed_tokens = p.parse()

    print(parsed_tokens)
    rw = ReadTokensToWriteIntoHtml(parsed_tokens)
    rw.debug()
