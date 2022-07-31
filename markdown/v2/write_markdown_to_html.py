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
            html.append(self.recurse(parsed_token))
        DEBUG("HTML")
        DEBUG('\n'.join(html))
        return '\n'.join(html)
    def recurse(self, token):
        DEBUG("BEGIN RECURSIVE")
        if token.type_ == ParsedTokenType.IMG:
           IMG = unwind_image(token.value) 
           return IMG
        elif token.type_ == ParsedTokenType.H1:
            output = []
            output.append('<h1>')
            for val in token.value:
                inner = self.recurse(val)
                output.append(inner)
            output.append('</h1>')
            return ''.join(output)
        elif token.type_ == ParsedTokenType.P:
            output = []
            DEBUG("PARSING Paragraph")
            output.append('<p>')
            for val in token.value:
                inner = self.recurse(val)
                output.append(inner)
            output.append('</p>')
            return ''.join(output)
        elif token.type_ == ParsedTokenType.LI:
            output = []
            DEBUG("PARSING Paragraph")
            output.append('<li>')
            for val in token.value:
                inner = self.recurse(val)
                output.append(inner)
            output.append('</li>')
            return ''.join(output)
        elif token.type_ == ParsedTokenType.UL:
            output = []
            DEBUG("PARSING UL")
            output.append("<ul>")
            for val in token.value:
                DEBUG("UL CHILD")
                DEBUG(val)
                inner = self.recurse(val)
                output.append(inner)
            output.append("</ul>")
            return ''.join(output)
        elif not is_block_element(token.type_):
            return token.value
        output = []
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
    debug_string = rw.debug()
    Path('./result.html').write_text(debug_string)
