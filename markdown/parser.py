import sys
from pathlib import Path

#============START============

def main():
    if not len(sys.argv) == 2:
        print('Provide a file name please')
        return
    file_name = sys.argv[1]
    string = Path(file_name).read_text()
    p = MarkDownParser(string)
    p.run()
    print('finished')



#============HELPERS============

def token(type, char):
    return { 'type': type, 'char': char }

TOKENS = {
        'heading': 'heading',
        'ol': 'ol',
        'ul': 'ul',
        'p': 'p',
        'img': 'img',
        'a_tag': 'a_tag',
        }

#============PARSER============

class MarkDownParser:
    def __init__(self, string):
        self.string = string
        self.cur = 0
        self.len = len(self.string)
        self.tokens = []
        self.html = []
        self.char = None
        self.line_meta = {
                'start_line': True,
                'white_space_count': 0,
                'previous_type': None,
                'nested': False,
        }

    
    def run(self):
        self.char = self.string[0]
        while not self.eof() and self.char is not None:
            # if self.line_meta.start_line and self.is_whitespace():
            #    self.consume_whitespace()
            if self.char == '-' or self.char == '*':
                self.line_meta['start_line'] = False
                lines = []
                IN = True
                while IN:
                    line = self.consume_line()
                    lines.append(f'  <li>{line}</li>')
                    self.char = self.get_char()
                    if self.char != '-':
                        print('out')
                        IN = False
                items = '\n'.join(lines)
                self.html.append(f'<ul>\n{items}\n</ul>')
            elif self.char == '#':
                num_hashes = 0
                while self.char == '#':
                    self.char = self.get_char()
                    num_hashes +=1
                line = self.consume_line()
                self.html.append(f'<h{num_hashes}>{line}</h{num_hashes}>')
            elif self.char == '[':
                print(self.char)
            elif self.char == '>':
                line = self.consume_line()
                self.html.append(f'<blockquote>{line}</blockquote>')

            elif self.char == '\n':
                self.sline = True

            self.char = self.get_char()           
        self.html.append('\n')
        writable = Path('./res.html')
        writable.write_text('\n'.join(self.html))
    def consume_whitespace(self):
        while not self.eof() and self.char != ' ' and self.char != '\t':
            self.char = self.get_char()
            self.cur += 1
            if self.char == '\n':
                self.sline = True
                break
            if self.char != ' ' or self.char != '\t':
                break

    def consume_line(self):
        self.char = self.get_char()
        chars = []
        while self.char != '\n': 
            chars.append(self.char)
            self.char = self.get_char()
        return ''.join(chars).strip()

    def get_char(self):
       self.cur +=1
       if self.eof():
           return None
       self.char = self.string[self.cur]
       return self.char

    def is_whitespace(self):
        return self.char.isspace()

    def peek(self):
        if self.cur + 1 < self.len:
            return self.string[self.cur + 1]
        return False

    def eof(self):
       return self.cur >= self.len


if __name__ == '__main__':
    main()
