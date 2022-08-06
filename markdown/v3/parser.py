from lexer import Lexer, TokenType 
from pathlib import Path 

def header(header_type, text):
    return f'<h{header_type}>{text}</h{header_type}>'

def paragraph(text):
    return f'<p>{text}</p>'

def li(text):
    return f'<li>{text}</li>'

def ul(list_items):
    return f'<ul>{list_items}</ul>'

def bold(text):
    return f'<strong>{text}</strong>'

def italic(text):
    return f'<i>{text}</i>'

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
            elif self.current_token.type_ == TokenType.LeftBracket:
                paragraph = self.parse_paragraph()
                self.html.append(paragraph)
            elif self.current_token.type_ == TokenType.Dash:
                print('begin')
                list_items = self.find_all_list_items()
                list_items = [self.parse_block(line) for line in list_items]
                list_items_string = '\n'.join([li(test) for test in list_items])
                ul_tag  = ul(list_items_string)
                self.html.append(ul_tag)
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
            elif token.type_ == TokenType.Star:
                print("star")
                print(tokens[index:])
                if tokens[index+1].type_ == TokenType.Star:
                    index, bold, error = self.try_parse_bold(index, tokens)
                    if error:
                        raise Exception("not bold!")
                    parsed_html.append(bold)
                else:
                    index, italic, error = self.try_parse_italic(index, tokens)
                    if error:
                        raise Exception("not an italic!")
                    parsed_html.append(italic)
            elif token.type_ == TokenType.Shebang and tokens[index+1].type_ == TokenType.LeftBracket:
                print('image parsing')
                index, img_or_text, error = self.try_parse_img(index, tokens)
                if error:
                    raise Exception("not an image!")
                parsed_html.append(img_or_text)
            else:
                parsed_html.append(token.value)
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

    def try_parse_bold(self, index, tokens):
        index += 1 
        text = []
        while index < len(tokens):
            token = tokens[index]
            if token.type_ == TokenType.Star and tokens[index+1].type_ == TokenType.Star:
                index +=2
                return index, bold(''.join(text)), False
            else:
                text.append(token.value)
            index += 1

        return index, bold(''.join(text)), False

    def try_parse_italic(self, index, tokens):
        index += 1 
        text = []
        while index < len(tokens):
            token = tokens[index]
            if token.type_ == TokenType.Star:
                index += 1
                return index, italic(''.join(text)), False
            else:
                text.append(token.value)
            index += 1

        return index, italic(''.join(text)), False
    def consume_while(self, condition):
        while condition():
            self.next()

    def find_all_list_items(self):
        self.next()
        list_items = []
        list_item  = []
        print('debug list items')
        print(self.tokens[self.index:])
        while not self.eof():
            if self.current_token.type_ == TokenType.NewLine:
                list_items.append(list_item)
                print('here')
                print(self.current_token.type_)
                print(self.next_token.type_)
                self.next()
                print(self.current_token.type_)
                print(self.next_token.type_)
                if self.current_token.type_ == TokenType.Dash: # should try and parse until newline
                    list_item = []
                else:
                    return list_items
            else:
                list_item.append(self.current_token)
            self.next()
        return list_items
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
