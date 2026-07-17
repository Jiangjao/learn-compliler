#!/usr/bin/python
# Write Python 3 code in this online editor and run it.
import re

# 1. 词法分析：将字符串转为 Token 流
class Lexer:
    def __init__(self, text):
        self.tokens = re.findall(r'\d+|[+\-*/()]', text)
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        token = self.peek()
        self.pos += 1
        return token

# 2. 语法分析：递归下降解析
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

    def parse(self): # 入口：Expr
        return self.expr()

    def expr(self):  # Expr -> Term { (+|-) Term }
        node = self.term()
        while self.lexer.peek() in ('+', '-'):
            op = self.lexer.consume()
            right = self.term()
            node = (op, node, right) # 构建 AST 节点
        return node

    def term(self):  # Term -> Factor { (*|/) Factor }
        node = self.factor()
        while self.lexer.peek() in ('*', '/'):
            op = self.lexer.consume()
            right = self.factor()
            node = (op, node, right)
        return node

    def factor(self): # Factor -> Number | ( Expr )
        token = self.lexer.consume()
        if token == '(':
            node = self.expr()
            self.lexer.consume() # 消耗 ')'
            return node
        return int(token) # 直接返回数字节点

# 3. 计算 AST (求值器)
def evaluate(node):
    if isinstance(node, int): return node
    op, left, right = node
    if op == '+': return evaluate(left) + evaluate(right)
    if op == '-': return evaluate(left) - evaluate(right)
    if op == '*': return evaluate(left) * evaluate(right)
    if op == '/': return evaluate(left) / evaluate(right)

# --- 测试 ---
# text = "3 + 5 * ((((10 - 2)))))"
text = "3 + 5 * (10 - 2)"
lexer = Lexer(text)
print(lexer.tokens)
parser = Parser(lexer)
ast = parser.parse()

print(f"AST 结构: {ast}")
print(f"计算结果: {evaluate(ast)}")

# 注意正则无法匹配各种可能的算术表达式
# ['3', '+', '5', '*', '(', '10', '-', '2', ')']
# AST 结构: ('+', 3, ('*', 5, ('-', 10, 2)))
# 计算结果: 43
