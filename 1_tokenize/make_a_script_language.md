要将**《语法分析（三）：实现一门简单的脚本语言》**这一章切实地写下去，你需要引导读者实现从“解析单个表达式”到“执行一个完整的程序语句序列”的跨越。

以下是这一章最合理的**行文框架与代码实现路径**。你可以按照这六个步骤逐步展开：

---

### 第一步：明确本章的目标（Goal）

首先，告诉读者这门脚本语言的“最小可行性产品”（MVP）长什么样。我们要让下面这段代码能真正跑起来并输出结果：

```javascript
let a = 10;
let b = a * 2 + 5;
print(b); // 期望输出: 25
```
为了达成这个目标，我们需要把之前的“表达式解析器”升级为能够处理“语句（Statements）”和“状态（Environment）”的**解释器**。

---

### 第二步：扩展语法规则（EBNF）

在上一章中，我们只有 `Expression`。现在，我们需要引入 **“语句（Statement）”** 和 **“程序（Program）”** 的概念。

用文法（EBNF）表示如下：
```text
Program    -> Statement* EOF
Statement  -> VarDeclStmt | PrintStmt | ExpressionStmt

VarDeclStmt -> "let" Identifier "=" Expression ";"
PrintStmt   -> "print" "(" Expression ")" ";"
ExpressionStmt -> Expression ";"
```
* **解释**：一个程序由多条语句组成。语句和表达式的区别在于：表达式计算出一个值，而语句执行一个动作（如声明变量、打印），通常不返回值。

---

### 第三步：设计 AST 节点与运行时环境（Environment）

除了之前算术运算的节点外，我们需要新增语句节点。同时，我们需要一个用来存放变量的地方——**运行时环境**。

#### 1. 新增 AST 节点
```python
# 变量声明语句节点： let name = initializer;
class VarDeclNode:
    def __init__(self, name: str, initializer):
        self.name = name          # 变量名，如 "a"
        self.initializer = initializer  # 初始值表达式节点

# 打印语句节点： print(expression);
class PrintNode:
    def __init__(self, expression):
        self.expression = expression  # 需要打印的表达式节点
```

#### 2. 实现运行时环境（作用域）
变量必须存储在内存中。我们可以实现一个简单的 `Environment` 类，内部用一个字典来管理变量：

```python
class Environment:
    def __init__(self):
        self.values = {}

    def define(self, name: str, value):
        """定义/声明变量"""
        self.values[name] = value

    def get(self, name: str):
        """获取变量值"""
        if name in self.values:
            return self.values[name]
        raise NameError(f"未定义的变量: '{name}'")
```

---

### 第四步：升级解析器（Parser）

现在，我们需要在解析器中实现“自顶向下”解析语句的逻辑。

```python
class Parser:
    # ... 保留之前的 parse_expression, parse_term, parse_primary ...

    def parse_program(self) -> list:
        """主入口：解析整个程序"""
        statements = []
        while not self.is_at_end():
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        """解析单条语句"""
        if self.match("LET"):
            return self.parse_var_declaration()
        if self.match("PRINT"):
            return self.parse_print_statement()
        return self.parse_expression_statement()

    def parse_var_declaration(self):
        """解析变量声明 let x = ...;"""
        name = self.consume("IDENTIFIER", "期待变量名").value
        self.consume("EQUAL", "期待 '='")
        initializer = self.parse_expression()
        self.consume("SEMICOLON", "期待分号 ';'")
        return VarDeclNode(name, initializer)

    def parse_print_statement(self):
        """解析打印语句 print(...);"""
        self.consume("LEFT_PAREN", "期待 '('")
        expr = self.parse_expression()
        self.consume("RIGHT_PAREN", "期待 ')'")
        self.consume("SEMICOLON", "期待分号 ';'")
        return PrintNode(expr)
```

---

### 第五步：实现求值器/解释器（Evaluator）

有了 AST 和运行时环境后，我们只需要写一个**求值函数**来深度优先遍历这棵树。

这里我们使用最直观的模式匹配（或类型判断）来编写 `evaluate` 函数：

```python
def evaluate(node, env: Environment):
    # 1. 处理字面量节点
    if isinstance(node, LiteralNode):
        return node.value

    # 2. 处理变量引用节点（从环境里查值）
    if isinstance(node, VariableRefNode):
        return env.get(node.name)

    # 3. 处理二元表达式节点（加减乘除）
    if isinstance(node, BinaryOpNode):
        left_val = evaluate(node.left, env)
        right_val = evaluate(node.right, env)
        if node.op == '+': return left_val + right_val
        if node.op == '-': return left_val - right_val
        if node.op == '*': return left_val * right_val
        if node.op == '/': return left_val / right_val

    # 4. 处理变量声明语句（向环境里写入值）
    if isinstance(node, VarDeclNode):
        val = evaluate(node.initializer, env)
        env.define(node.name, val)
        return None

    # 5. 处理打印语句
    if isinstance(node, PrintNode):
        val = evaluate(node.expression, env)
        print(val) # 调用宿主语言的 print 输出
        return None
```

---

### 第六步：串联并运行（REPL 或脚本执行）

最后，将词法分析（Lexer）、语法分析（Parser）和解释器（Evaluator）串联起来，让用户看到成果。

```python
def run_script(source_code: str):
    # 1. 词法分析
    lexer = Lexer(source_code)
    tokens = lexer.scan_tokens()

    # 2. 语法分析
    parser = Parser(tokens)
    statements = parser.parse_program()  # 得到语句列表 (ASTs)

    # 3. 初始化全局环境并执行
    env = Environment()
    for stmt in statements:
        evaluate(stmt, env)

# --- 测试运行 ---
code = """
let a = 10;
let b = a * 2 + 5;
print(b);
"""
run_script(code)  # 控制台将打印出：25
```

---

### 编写此文的写作建议

1. **强调“状态”的引入**：在文章开头指出，计算器是没有“记忆”的，而脚本语言之所以是脚本语言，是因为有了 `Environment`（环境/上下文），让程序有了“状态（State）”。
2. **结合上一章的调用栈知识**：在介绍 `evaluate` 递归时，顺便提一句：“还记得我们上一章讲的调用栈深度吗？求值器在这里也是自顶向下递归，先计算叶子节点（数字），再逐步折返计算出整棵树的值。”
3. **提供完整的演练代码**：在文章末尾提供一个几十行、可以直接运行的完整 Python 或 TypeScript 示例，读者只要复制黏贴就能在本地跑起来。这种即时反馈能带来巨大的成就感。
