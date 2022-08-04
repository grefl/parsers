from pathlib import Path
from parser import Parser, ParsedTokenType
from lexer import Lexer, TokenType

def DEBUG(*vals): 
    formatted = " ".join([str(v) for v in vals])
    print(f"[DEBUG]: {formatted}")

def is_block_element(token_type):
    return token_type == ParsedTokenType.IMG or token_type == ParsedTokenType.H1 or token_type == ParsedTokenType.P or token_type == ParsedTokenType.UL

def get_header_type(token_type):
    if token_type == ParsedTokenType.H1:
        return 1 
    elif token_type == ParsedTokenType.H2:
        return 2 
    elif token_type == ParsedTokenType.H3:
        return 3 
    elif token_type == ParsedTokenType.H4:
        return 4 
    elif token_type == ParsedTokenType.H5:
        return 5 
    return 6

def is_header(token_type):
    return token_type == ParsedTokenType.H1 or token_type == ParsedTokenType.H2 \
        or token_type == ParsedTokenType.H3 or token_type == ParsedTokenType.H4 \
        or token_type == ParsedTokenType.H5 or token_type == ParsedTokenType.H6 \

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
            url = ''
            index +=1
            val = values[index]
            while index < len(values) and values[index].type_ != TokenType.RightParen:
                DEBUG("THE URL", url)
                url += values[index].value
                index +=1

            DEBUG("APPEND URL", url)
            output.append(f'src="{url}"')
        index +=1
    output.append('/>')
    return ''.join(output)
def unwind_ATag(values):
    output = []
    output.append('<a ')
    index = 0
    text = []
    while index < len(values):
        val = values[index]
        if val.type_ == TokenType.LeftBracket:
            index +=1
            while index < len(values):
                if values[index].type_ == TokenType.RightBracket:
                    break
                print(text)
                text.append(values[index].value)
                index +=1
        elif val.type_ == TokenType.LeftParen:
            url = ''
            index +=1
            val = values[index]
            while index < len(values):
                if values[index].type_ == TokenType.RightParen:
                    break
                url += values[index].value
                index +=1


            output.append(f'href="{url}"')
        index +=1
    output.append('>')
    output.append(''.join(text))
    output.append('</a>')
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
        elif is_header(token.type_):
            output = []
            header_type = get_header_type(token.type_) 
            DEBUG("HEEEEEEEEERE")
            DEBUG(token.type_)
            output.append(f'<h{header_type}>')
            for val in token.value:
                inner = self.recurse(val)
                output.append(inner)
            output.append(f'</{header_type}>')
            return ''.join(output)
        elif token.type_ == ParsedTokenType.A:
            A = unwind_ATag(token.value)
            return A
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
