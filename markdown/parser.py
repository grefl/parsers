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


def peek(text, i):
    if i+ 1 < len(text):
        return text[i+ 1]
    return False
def next_char(text, i):
    if i + 1 < len(text):
        return text[i + 1]
    return None


#============PARSER============

class MarkDownParser:
    def __init__(self, string):
        self.string = string
        self.cur = 0
        self.len = len(self.string)
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
            if self.char == '-' or self.char == '*' or self.char == '+':
                self.line_meta['start_line'] = False
                lines = []
                IN = True
                list_type = self.char
                line = self.consume_line()
                lines.append(f'  <li>{self.parse_line(line)}</li>')
                while IN:
                    if self.peek() != list_type:
                        IN = False
                        break
                    self.char = self.get_char()
                    line = self.consume_line()
                    lines.append(f'  <li>{self.parse_line(line)}</li>')
                items = '\n'.join(lines)
                self.html.append(f'<ul>\n{items}\n</ul>')
            elif self.char == '#':
                num_hashes = 0
                while self.char == '#':
                    self.char = self.get_char()
                    num_hashes +=1
                line = self.consume_line()
                self.html.append(f'<h{num_hashes}>{self.parse_line(line)}</h{num_hashes}>')
            elif self.char == '[':
                curr_char = self.char
                line = self.consume_line()
                parsed_line = self.parse_line(curr_char + line)
                self.html.append(parsed_line)
            elif self.char == '>':
                line = self.consume_line()
                self.html.append(f'<blockquote>{self.parse_line(line)}</blockquote>')

            elif self.char == '\n':
                print('new line')
                # self.cur +=1
            elif self.char == '`' and peek(self.string, self.cur) == '`' and peek(self.string, self.cur + 1) == '`':
                lines = []
                line = self.consume_line()
                lines.append(line)
                while self.char and not (self.char == '`' and peek(self.string, self.cur) == '`' and peek(self.string, self.cur + 1) == '`'):
                   save_char = self.char
                   line = self.consume_line()
                   lines.append(save_char + line)
                   self.char = self.get_char()
                code = '\n'.join(lines)
                self.html.append(f'<pre><code>\n{code}\n</code></pre>')
            elif self.char == '`':
                lines = []
                line = self.consume_line()
                lines.append(line)
                self.char = self.get_char()
            else:
                save_char = self.char
                print(save_char)
                line = self.consume_line(strip = False)
                self.html.append(f'<p>{self.parse_line(save_char + line)}</p>')
            self.char = self.get_char()           
        self.html.append('\n')
        writable = Path('./res.html')
        writable.write_text('\n'.join(self.html))

    def consume_whitespace(self):
        while not self.eof() and self.char != ' ' and self.char != '\t':
            self.char = self.get_char()
            self.cur += 1
            if self.char == '\n':
                self.line_meta.start_line = True
                break
            if self.char != ' ' or self.char != '\t':
                break
    def parse_line(self,text):
        i = 0
        char = text[i]
        state = { 'IN': False, 'type': None, 'offset': { 'img': 2, 'a': 1 }, 'start_index': -1, 'next_index': -1 }
        chars = []
        while i < len(text):
            char = text[i]
            if char == '[' or char == '!':
                type = 'img' if char == '!' else 'a'
                state = {**state, 'IN': True, 'type': type, 'start_index': i}
                failed = False
                temp_chars = []
                j = 0
                while state['IN'] and i + j < len(text):
                    if char == ']' and peek(text, i + j) == '(':
                        temp_chars.append(char)
                        state['next_index'] = j 
                    elif char == ']' and peek(text, i + j) != '(':
                        temp_chars.append(char)
                        for c in temp_chars:
                            chars.append(c)
                        i += j 
                        state['IN'] = False
                        break
                    elif char == ')' and state['next_index'] != -1:
                        m_index = state['next_index']
                        offset = state['offset'][state['type']]
                        text = temp_chars[offset:m_index]
                        text = ''.join(text)
                        string = None
                        url = temp_chars[m_index +2:]
                        url = ''.join(url)
                        if state['type'] == 'img':
                            string = f'<img alt="{text}" src="{url}" />'
                        else:
                            string = f'<a href="{url}">{text}</a>'
                        chars.append(string)
                        state['IN'] = False
                        i += j
                        break
                    else:
                        temp_chars.append(char)
                    j +=1
                    char = text[i + j]
            elif char == '`':
                start = i
                temp_chars = []
                temp_chars.append(char)
                j = 1
                if i + j >= len(text):
                    break
                char = text[i + j]
                while i + j < len(text) and char != '`': 
                   temp_chars.append(char) 
                   j += 1
                   char = text[i+j]

                if char == '`':
                    text = ''.join(temp_chars[1:])
                    string = f'<pre><code>{text}</code></pre>'
                    chars.append(string)
                else:
                    for c in temp_chars:
                        chars.append(c)
                i += j
            elif char == "*":
                start = i 
                temp_chars = []
                temp_chars.append(char)
                j = 0
                peeked = peek(text, i)
                if not peeked:
                    chars.append(char)
                    i +=1
                    break

                type = 'strong' if char == peeked else 'em'
                if type == 'strong':
                    j += 1 
                char = next_char(text, i + j) 
                print(f'char -> {char}')
                while char and char != '*':
                    temp_chars.append(char)
                    j +=1
                    char = next_char(text, i + j)     
                if not char:
                    for c in temp_chars:
                        chars.append(c)
                else:
                    joined = ''.join(temp_chars[1:])
                    string = f'<{type}>{joined}</{type}>'
                    chars.append(string)
                i += (j + 2)
                print(len(text), i)
            else:
                chars.append(char)
                i += 1
        return ''.join(chars)
    
    def consume_line(self, strip = True):
        self.char = self.get_char()
        chars = []
        while self.char and self.char != '\n': 
            chars.append(self.char)
            self.char = self.get_char()
        if strip:
            return ''.join(chars).strip()
        return ''.join(chars)

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
