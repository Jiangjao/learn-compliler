# 1. 定义 AST 节点
class NumberNode:
    def __init__(self, value):
        self.value = value

class BinaryOpNode:
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

# 2. 词法分析器
class Lexer:
    def __init__(self, text):
        self.tokens = text.replace('+', ' + ').replace('*', ' * ').split()
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self):
        token = self.peek()
        self.pos += 1
        return token

# 3. 语法分析器
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer

    def parse_additive(self):
        node = self.parse_multiplicative()
        while self.lexer.peek() == '+':
            self.lexer.consume()
            right = self.parse_multiplicative()
            node = BinaryOpNode(node, '+', right)
        return node

    def parse_multiplicative(self):
        node = NumberNode(int(self.lexer.consume()))
        while self.lexer.peek() == '*':
            self.lexer.consume()
            right = NumberNode(int(self.lexer.consume()))
            node = BinaryOpNode(node, '*', right)
        return node

# 4. 可视化求值器 (带有你要求的输出逻辑)
def evaluate(node, indent=0):
    space = "    " * indent
    
    # 如果是数字节点
    if isinstance(node, NumberNode):
        print(f"{space}Calculating: IntLiteral")
        print(f"{space}Result: {node.value}")
        return node.value
    
    # 如果是运算节点
    if isinstance(node, BinaryOpNode):
        op_name = "AdditiveExp" if node.op == '+' else "MulticativeExp"
        print(f"{space}Calculating: {op_name}")
        
        # 递归计算
        left_val = evaluate(node.left, indent + 1)
        right_val = evaluate(node.right, indent + 1)
        
        # 计算结果
        res = left_val + right_val if node.op == '+' else left_val * right_val
        print(f"{space}Result: {res}")
        return res

# --- 运行测试 ---
if __name__ == "__main__":
    code = "3 * 5 + 7"
    print(f"解析表达式: {code}\n")
    
    # 1. 解析生成 AST
    lexer = Lexer(code)
    parser = Parser(lexer)
    ast = parser.parse_additive()
    
    # 2. 打印追踪过程
    print("Calculating: AdditiveExp") # 根节点说明
    final_res = evaluate(ast, indent=1)
    print(f"\n最终计算结果: {final_res}")
