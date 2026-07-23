import re

# 1. 内存符号表（HashMap）
memory = {}

# 2. 词法分析器（把字符串切成 Token）
def tokenize(text):
    token_patterns = [
        ('VAR', r'[a-zA-Z_][a-zA-Z0-9_]*'),
        ('NUM', r'\d+'),
        ('ASSIGN', r'='),
        ('PLUS', r'\+'),
        ('MINUS', r'-'),
        ('MUL', r'\*'),
        ('DIV', r'/'),
        ('SEMI', r';'),
        ('SKIP', r'\s+'),
    ]
    regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_patterns)
    tokens = []
    for match in re.finditer(regex, text):
        kind = match.lastgroup
        value = match.group(kind)
        if kind == 'SKIP': continue
        if kind == 'NUM': value = int(value)
        tokens.append((kind, value))
    return tokens

# 3. 带回溯与优先级的解析器
class BacktrackParser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def save_state(self): return self.pos
    def restore_state(self, state): self.pos = state

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected_kind=None):
        token = self.peek()
        if not token or (expected_kind and token[0] != expected_kind):
            return None
        self.pos += 1
        return token

    # 顶层解析入口：带回溯试错
    def parse(self):
        checkpoint = self.save_state()
        
        # 尝试规则 A: 赋值语句 (VAR '=' 表达式)
        var_token = self.consume('VAR')
        if var_token and self.consume('ASSIGN'):
            expr = self.parse_expr()
            if expr:
                self.consume('SEMI')
                return ('=', var_token[1], expr)

        # ❌ 规则 A 失败，触发【回溯】！
        print("   [回溯发生] 尝试规则 A 失败，回滚指针...")
        self.restore_state(checkpoint)
        return None

    def parse_expr(self):
        node = self.parse_term()
        while self.peek() and self.peek()[0] in ('PLUS', 'MINUS'):
            op = self.consume()
            node = (op[1], node, self.parse_term())
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.peek() and self.peek()[0] in ('MUL', 'DIV'):
            op = self.consume()
            node = (op[1], node, self.parse_factor())
        return node

    def parse_factor(self):
        token = self.consume()
        if not token: return None
        if token[0] == 'NUM': return token[1]
        if token[0] == 'VAR': return token[1]
        return None

# 4. 求值器
def evaluate(node):
    if isinstance(node, int): return node
    if isinstance(node, str):
        if node not in memory: raise NameError(f"变量未定义: {node}")
        return memory[node]
    op, left, right = node
    if op == '=':
        val = evaluate(right)
        memory[left] = val
        return val
    if op == '+': return evaluate(left) + evaluate(right)
    if op == '-': return evaluate(left) - evaluate(right)
    if op == '*': return evaluate(left) * evaluate(right)
    if op == '/': return evaluate(left) / evaluate(right)

# ==================== 测试运行 ====================
memory['age'] = 5
print("【初始状态】内存符号表:", memory)

code = "age = age + 10 * 2;"
print(f"执行代码: {code}")

tokens = tokenize(code)
parser = BacktrackParser(tokens)
ast = parser.parse()

print("【解析生成的 AST】:", ast)
result = evaluate(ast)
print("【计算结果】:", result)
print("【最终内存符号表】:", memory)
