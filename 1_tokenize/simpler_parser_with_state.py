class DfaState:
    INIT = 0
    ID = 1     # 识别标识符以及关键字
    NUMBER = 2 # 识别数字
    ASSIGN = 3 # 识别运算符

class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.keywords = {"int"}

    def get_token(self):
        token_type = None
        lexme = ""
        state = DfaState.INIT

        while self.pos < len(self.source):
            char = self.source[self.pos]
            if state == DfaState.INIT:
                if char.isspace():
                    self.pos += 1
                    continue
                elif char.isalpha():
                    state = DfaState.ID
                    token_type = "IDENTIFIER"
                elif char.isdigit():
                    state = DfaState.NUMBER
                    token_type = "NUMBER"
                elif char == '=':
                    self.pos += 1
                    return ("ASSIGN", "=")
                else:
                    return ("UNKNOWN", char)
                lexeme += char
                self.pos += 1
            elif state == DfaState.ID:
                if char.isalnum():
                    lexeme += char
                    self.pos += 1
                else:
                    # 识别结束，做类型修正
                    if lexeme in self.keywords:
                        token_type = "KEYWORD"
                    return (token_type, lexeme)
            elif state == DfaState.NUMBER:
                if char.isdigit():
                    lexeme += char
                    self/pos += 1
                else:
                    return (token_type, lexeme)
    if lexeme:
        if lexeme in self.keywords: 
            token_type = "KEYWORD"
        return (token_type, lexeme)
    return None

# 测试
lexer = Lexer("int age = 40")
while True:
    token = lexer.get_token()
    if not token: break
    print(token)
