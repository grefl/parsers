from lexer import Lexer, TokenType 
from pathlib import Path 

def header(header_type, text):
    return f'<h{header_type}>{text}</h{header_type}>'

def paragraph(text):
    return f'<p>{text}</p>'

def a_tag(url, text):
    return f'<a url="{url}">{text}</a>'

def img(src, alt):
    return f'<img src="{src}" alt="{alt}" />'

class Parser:
    def __init__(self, lexed_tokens):
        self.tokens = lexed_tokens
        self.current_token = None
        self.next_token    = None
        self.html = []
        self.index = 0

    def next(self):
        self.current_token = self.next_token
        self.index +=1
        if self.index >= self.tokens_len():
            self.next_token = None
        else:
            self.next_token = self.tokens[self.index]
        return self.current_token

    def tokens_len(self):
        return len(self.tokens)

    def eof(self):
        return self.index >= self.tokens_len() 

    def peek(self, amount):
        if self.index + amount >= self.tokens_len():
            return None
        return self.tokens[self.index + amount]
    
    def parse_header(self):
        h1s = []
        parsing_headers = True
        tokens = []
        while not self.eof():
            if parsing_headers and self.current_token.type_ == TokenType.Hash:
                h1s.append(self.current_token.value)
            elif self.current_token.type_ == TokenType.NewLine:
                self.next()
                return header(len(h1s), ''.join(self.parse_block(tokens)))
            else:
                tokens.append(self.current_token)
                parsing_headers = False
            self.next()
        return header(len(h1s), ''.join(tokens))

    def parse_paragraph(self):
        tokens = []
        while not self.eof():
            if self.current_token.type_ == TokenType.NewLine:
                self.next()
                return paragraph(''.join(self.parse_block(tokens)))
            else:
                tokens.append(self.current_token)
            self.next()
        return paragraph(self.parse_block(tokens))

    def parse(self):

        self.next()
        self.next()
        while not self.eof():
            if self.current_token.type_ == TokenType.Hash:
                print("it's a hash")
                header = self.parse_header()
                print(header)
                self.html.append(header)
            elif self.current_token == TokenType.LeftBracket:
                print('unimplemented yo') 
            else:
                paragraph = self.parse_paragraph()
                self.html.append(paragraph)
            self.next()
        return '\n'.join(self.html)

    def parse_block(self, tokens):
        index = 0
        end = len(tokens)
        parsed_html = []
        while index < end:
            token = tokens[index]
            if token.type_ == TokenType.LeftBracket:
                index, url_or_text, error = self.try_parse_url(index, tokens)
                if error:
                    raise Exception("not a url, oh no!")
                parsed_html.append(url_or_text)
            elif token.type_ == TokenType.Shebang and tokens[index+1].type_ == TokenType.LeftBracket:
                print('image parsing')
                index, img_or_text, error = self.try_parse_img(index, tokens)
                if error:
                    raise Exception("not an image!")
                parsed_html.append(img_or_text)
            index +=1
        return ''.join(parsed_html)

    def try_parse_url(self, index, tokens):
        index += 1
        text = []
        finished_parsing_text = False
        url = []
        while index < len(tokens):
            token = tokens[index]
            
            if token.type_ == TokenType.RightBracket and tokens[index+1].type_ == TokenType.LeftParen:
                finished_parsing_text = True 
                index +=1
            elif not finished_parsing_text:
                text.append(token.value)
            elif token.type_ == TokenType.RightParen:
                return index, a_tag(''.join(url), ''.join(text)), False
            else:
                url.append(token.value)
            index += 1

        return index, a_tag(''.join(url), ''.join(text)), False

    def try_parse_img(self, index, tokens):
        index += 2 
        alt_text = []
        finished_parsing_text = False
        url = []
        while index < len(tokens):
            token = tokens[index]
            
            if token.type_ == TokenType.RightBracket and tokens[index+1].type_ == TokenType.LeftParen:
                finished_parsing_text = True 
                index +=2
                continue
            elif not finished_parsing_text:
                alt_text.append(token.value)
            elif token.type_ == TokenType.RightParen:
                return index, img(''.join(url), ''.join(alt_text)), False
            else:
                url.append(token.value)
            index += 1

        return index, img(''.join(url), ''.join(text)), False
def main():
    file_string = Path('./temp').read_text()
    l = Lexer(file_string)
    lexed_tokens = l.lex()
    p = Parser(lexed_tokens)
    html = p.parse()
    print(f"{html=}")
    Path('./debug.html').write_text(html)

if __name__ == "__main__":
    main()
