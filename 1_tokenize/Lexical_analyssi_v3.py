# 1. 定义 AST 节点类型
class NumberNode:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"IntLiteral({self.value})"

class BinaryOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def __repr__(self):
        return f"({self.left} {self.op} {self.right})"

# 2. 词法分析器 (Lexer)
class Lexer:
    def __init__(self, text):
        # 简单的正则分词：提取数字和运算符
        self.tokens = text.replace('+', ' + ').replace('*', ' * ').split()
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        token = self.peek()
        self.pos += 1
        return token

# 3. 语法分析器 (Parser - 递归下降)
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

    # AdditiveExp : MulticativeExp ( '+' MulticativeExp )*
    def parse_additive(self):
        node = self.parse_multiplicative()
        while self.lexer.peek() == '+':
            self.lexer.consume()  # 消耗 '+'
            right = self.parse_multiplicative()
            node = BinaryOpNode(node, '+', right)
        return node

    # MulticativeExp : IntLiteral ( '*' IntLiteral )*
    def parse_multiplicative(self):
        node = NumberNode(int(self.lexer.consume()))
        while self.lexer.peek() == '*':
            self.lexer.consume()  # 消耗 '*'
            right = NumberNode(int(self.lexer.consume()))
            node = BinaryOpNode(node, '*', right)
        return node

# 4. 求值器 (Evaluate)
def evaluate(node):
    if isinstance(node, NumberNode):
        return node.value
    if isinstance(node, BinaryOpNode):
        left = evaluate(node.left)
        right = evaluate(node.right)
        if node.op == '+': return left + right
        if node.op == '*': return left * right

# --- 测试 ---
code = "2 + 3 * 5"
lexer = Lexer(code)
parser = Parser(lexer)
ast = parser.parse_additive()

print(f"生成的 AST 结构: {ast}")
print(f"最终计算结果: {evaluate(ast)}")
