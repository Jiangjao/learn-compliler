# 1. 内存符号表（HashMap）
memory = {}

# 2. 简化的解释器/求值函数（支持数字、变量、加减乘除、赋值）
def evaluate(node):
    if isinstance(node, int): # 数字
        return node
    elif isinstance(node, str): # 变量名（如 'age'）
        if node not in memory:
            raise NameError(f"变量未定义: {node}")
        return memory[node]
    elif isinstance(node, tuple):
        op, left, right = node
        if op == '=':
            val = evaluate(right)
            memory[left] = val # 存入 HashMap
            return val
        elif op == '+': return evaluate(left) + evaluate(right)
        elif op == '-': return evaluate(left) - evaluate(right)
        elif op == '*': return evaluate(left) * evaluate(right)
        elif op == '/': return evaluate(left) / evaluate(right)

# 3. 模拟执行你的脚本语句：age = age + 10 * 2
# 用嵌套元组直接模拟已经解析好的 AST 结构：('=', 'age', ('+', 'age', ('*', 10, 2)))
ast = ('=', 'age', ('+', 'age', ('*', 10, 2)))

print("【初始状态】内存内存符号表:", memory)

# 步骤一：先给 age 赋个初始值 5
memory['age'] = 5
print("【步骤1: age = 5】内存符号表:", memory)

# 步骤二：执行 age = age + 10 * 2
result = evaluate(ast)
print("【步骤2: 执行计算】右侧计算结果:", result)
print("【步骤2: 最终内存符号表】", memory)
