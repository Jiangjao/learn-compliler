class TokenType:
    IDENTIFIER = "IDENTIFIER"
    KEYWORD_INT = "KEYWORD_INT"
    ASSIGN = "ASSIGN"
    INT_LITERAL = "INT_LITERAL"

class DfaState:
    INIT = 0
    ID = 1          # 通用标识符
    ID_INT1 = 2     # 匹配 'i'
    ID_INT2 = 3     # 匹配 'in'
    ID_INT3 = 4     # 匹配 'int'
    INT_LITERAL = 5 # 匹配数字

class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.token_text = ""
        self.tokens = []

    def is_blank(self, ch):
        return ch in [' ', '\t', '\n', '\r']

    def init_token(self, ch):
        """重置状态，并返回处理新字符后的初始状态"""
        self.token_text = ""
        if self.is_blank(ch):
            return DfaState.INIT
        elif ch.isalpha():
            self.token_text += ch
            return DfaState.ID_INT1 if ch == 'i' else DfaState.ID
        elif ch.isdigit():
            self.token_text += ch
            return DfaState.INT_LITERAL
        elif ch == '=':
            self.tokens.append((TokenType.ASSIGN, "="))
            return DfaState.INIT
        return DfaState.INIT

    def tokenize(self):
        state = DfaState.INIT
        
        for ch in self.source:
            if state == DfaState.INIT:
                if self.is_blank(ch): continue
                if ch.isalpha():
                    self.token_text += ch
                    state = DfaState.ID_INT1 if ch == 'i' else DfaState.ID
                elif ch.isdigit():
                    self.token_text += ch
                    state = DfaState.INT_LITERAL
                elif ch == '=':
                    self.tokens.append((TokenType.ASSIGN, "="))

            elif state == DfaState.ID_INT1:
                if ch == 'n':
                    self.token_text += ch
                    state = DfaState.ID_INT2
                elif ch.isalnum():
                    self.token_text += ch
                    state = DfaState.ID
                else:
                    self.tokens.append((TokenType.IDENTIFIER, self.token_text))
                    state = self.init_token(ch)

            elif state == DfaState.ID_INT2:
                if ch == 't':
                    self.token_text += ch
                    state = DfaState.ID_INT3
                elif ch.isalnum():
                    self.token_text += ch
                    state = DfaState.ID
                else:
                    self.tokens.append((TokenType.IDENTIFIER, self.token_text))
                    state = self.init_token(ch)

            elif state == DfaState.ID_INT3:
                # 只有在遇到空格或非字母数字时，才确认是 int 关键字
                if self.is_blank(ch) or not ch.isalnum():
                    self.tokens.append((TokenType.KEYWORD_INT, self.token_text))
                    state = self.init_token(ch)
                else:
                    self.token_text += ch
                    state = DfaState.ID

            elif state == DfaState.ID:
                if ch.isalnum():
                    self.token_text += ch
                else:
                    self.tokens.append((TokenType.IDENTIFIER, self.token_text))
                    state = self.init_token(ch)

            elif state == DfaState.INT_LITERAL:
                if ch.isdigit():
                    self.token_text += ch
                else:
                    self.tokens.append((TokenType.INT_LITERAL, self.token_text))
                    state = self.init_token(ch)
        
        # 处理缓冲区剩余内容
        if self.token_text:
            if state == DfaState.ID_INT3: self.tokens.append((TokenType.KEYWORD_INT, self.token_text))
            elif state == DfaState.ID: self.tokens.append((TokenType.IDENTIFIER, self.token_text))
            elif state == DfaState.INT_LITERAL: self.tokens.append((TokenType.INT_LITERAL, self.token_text))
            
        return self.tokens

# 测试
lexer = Lexer("int age = 45")
print(lexer.tokenize())
