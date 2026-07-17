class Lexer:
    def __init__(self, source):
        # 简化版词法分析：只匹配数字和运算符
        self.tokens = source.replace('+', ' + ').replace('*', ' * ').split()
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        token = self.peek()
        self.pos += 1
        return token

class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

    # 1. 加法层 (Additive)
    # 规则: multiplicativeExpression (Plus multiplicativeExpression)*
    def additive(self):
        node = self.multiplicative() # 先获取乘法节点
        while self.lexer.peek() == '+':
            self.lexer.consume() # 消耗 '+'
            right = self.multiplicative()
            node = ('+', node, right) # 向上构建加法节点
        return node

    # 2. 乘法层 (Multiplicative)
    # 规则: IntLiteral (Star IntLiteral)*
    def multiplicative(self):
        node = int(self.lexer.consume()) # 获取左操作数
        while self.lexer.peek() == '*':
            self.lexer.consume() # 消耗 '*'
            right = int(self.lexer.consume())
            node = ('*', node, right) # 向上构建乘法节点
        return node

# 测试
lexer = Lexer("2 + 3 * 5")
parser = Parser(lexer)
ast = parser.additive()

print(f"生成的 AST: {ast}")
# 解释一下 AST: ('+', 2, ('*', 3, 5))
# 这意味着先计算 3 * 5，再计算 2 + 结果
