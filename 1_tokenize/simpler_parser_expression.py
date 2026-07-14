#!/usr/bin/python
# Write Python 3 code in this online editor and run it.
class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.keywords = {"int"} # 简单关键字表

    def get_token(self):
        while self.pos < len(self.source) and self.source[self.pos].isspace():
            self.pos += 1
            
        if self.pos >= len(self.source): return None
        
        char = self.source[self.pos]
        
        # 1. 识别标识符/关键字
        if char.isalpha():
            lexeme = ""
            while self.pos < len(self.source) and self.source[self.pos].isalnum():
                lexeme += self.source[self.pos]
                self.pos += 1
            token_type = "KEYWORD" if lexeme in self.keywords else "IDENTIFIER"
            return (token_type, lexeme)
            
        # 2. 识别数字
        elif char.isdigit():
            lexeme = ""
            while self.pos < len(self.source) and self.source[self.pos].isdigit():
                lexeme += self.source[self.pos]
                self.pos += 1
            return ("NUMBER", lexeme)
            
        # 3. 识别运算符 (如 '=')
        elif char == '=':
            self.pos += 1
            return ("ASSIGN", "=")
            
        return ("UNKNOWN", char)

# 测试
source_code = "int age = 40"
lexer = Lexer(source_code)
while True:
    token = lexer.get_token()
    if not token: break
    print(token)
