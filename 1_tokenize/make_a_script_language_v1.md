基于你给出的语法大纲，我们将一步步推导并写下这部分内容。

在这部分，我们将解决脚本语言的核心问题：**从“只支持无状态计算”进化到“支持状态（变量与赋值）”**，并探讨手写解析器时最核心的算法设计挑战——**回溯与错误处理**。

---

### 一、 补充与扩展语法规则

为了支持变量和赋值，我们需要完整定义你给出的 `statement` 产生式，并同时**更新表达式规则**，让变量能够参与数学运算。

```antlr
// 1. 程序由一条或多条语句组成
program : statement+ ;

// 2. 语句的类型：变量声明、赋值、或者单纯的表达式
statement
    : intDeclaration
    | assignmentStatement
    | expressionStatement
    ;

// 3. 变量声明：int a; 或 int a = 10;
intDeclaration
    : 'int' Identifier ('=' expression)? ';'
    ;

// 4. 赋值语句：a = 20;
assignmentStatement
    : Identifier '=' expression ';'
    ;

// 5. 表达式语句：a + 5;
expressionStatement
    : expression ';'
    ;

// 6. 表达式（这里需要更新 primary，让表达式支持变量）
expression : additiveExpression ;

additiveExpression : multiplicativeExpression (('+' | '-') multiplicativeExpression)* ;

multiplicativeExpression : primaryExpression (('*' | '/') primaryExpression)* ;

primaryExpression
    : NumberLiteral
    | Identifier       // <--- 关键：变量名现在也是一种基础表达式
    | '(' expression ')'
    ;
```

---

### 二、 让脚本语言支持变量与解析赋值语句

要支持变量，我们需要解决两个工程问题：
1. **内存存储**：使用一个全局的 Map（即运行时环境 `Environment`）来保存变量名和它的值。
2. **AST 节点设计**：我们需要设计 `VarDeclNode`（声明）、`AssignmentNode`（赋值）和 `VariableRefNode`（引用）。

在解析时：
* 遇到 `intDeclaration`：在 AST 中记录声明，执行时在 Map 中开辟空间。
* 遇到 `assignmentStatement`：在 AST 中记录赋值，执行时去更新 Map 中对应的值。
* 遇到 `Identifier` 作为 `primaryExpression`：执行时去 Map 中读取它的值。

---

### 三、 理解递归下降算法中的“回溯（Backtracking）”

在手写递归下降解析器时，**回溯**是一个绕不开的概念。

#### 1. 为什么需要回溯？
看一下我们的两条规则：
* `assignmentStatement : Identifier '=' expression ';'`
* `expressionStatement  : expression ';'` 

当解析器读到一个 `Identifier`（比如变量名 `a`）时，它面临一个抉择：这到底是一个**赋值语句**（如 `a = 5;`），还是一个**表达式语句**（如 `a + 5;`，其中 `expression` 递归下去也会以 `Identifier` 开头）？

在**LL(1)**（只看当前一个 Token）的情况下，解析器是无法区分的。

#### 2. 回溯的工作原理
最朴素的解决方法就是“试错”：
1. 记录当前的 Token 位置（保存现场）。
2. **尝试**按照 `assignmentStatement` 的规则去解析。
3. 如果解析成功，皆大欢喜。
4. 如果中途发现不匹配（例如读完 `Identifier` 后发现下一个 Token 不是 `=` 而是 `+`），解析器就**把 Token 指针恢复到第一步记录的位置（回溯）**。
5. **尝试**按照下一个规则 `expressionStatement` 去解析。

---

### 四、 什么时候该回溯，什么时候该提示语法错误？

回溯虽然万能，但它有两个致命缺点：**效率低**（重复解析）和**报错定位极其困难**。
如果解析器总是盲目回溯，当用户写错代码时，解析器可能会默默回溯到最外层，然后弹出一个莫名其妙的“期待语句”错误，而不是精准指出哪一行少了个分号。

#### 核心法则：设立“提交点（Commit Point）”

我们需要区分两种失败：
* **分支选择失败（Speculative Failure）**：还没确定走哪条路，只是在尝试。此时**应该回溯**，换下一条路。
* **确定分支后的语法错误（Committed Failure）**：已经确定走这条路了，但用户写错了。此时**绝对不能回溯**，必须**立刻报错并终止/恢复**。

##### 案例分析 1：`intDeclaration`（变量声明）
* **规则**：`'int' Identifier ('=' expression)? ';'`
* **逻辑**：一旦解析器读到了 Token `int`，它就已经 **100% 确定**当前是一条变量声明语句。因为没有其他任何语句是以 `int` 开头的。
* **结论**：后续如果缺失了变量名，或者漏掉了分号，**不应该回溯**，必须立刻报错：“*Syntax Error: 期待变量名*”。

##### 案例分析 2：`assignmentStatement` 还是 `expressionStatement`？
* **规则**：`a = 5;` 对比 `a + 5;`
* **如何避免无谓的回溯（前瞻 Lookahead）**：
  我们其实不需要完整的“试错-回溯”。我们可以看**后一个 Token（Lookahead 2 / LL(2)）**：
  * 如果当前 Token 是 `Identifier`，且下一个 Token（Peek）是 `=`：我们就可以 **100% 确认**这是一条 `assignmentStatement`（进入提交点）。
  * 如果下一个 Token 不是 `=`：直接走 `expressionStatement`，**不需要进行任何物理上的回溯。**
* **一旦确定是赋值语句**：如果在 `=` 后面用户写了 `a = ;`（缺失表达式），立刻报错，不要回溯。

---

### 五、 终章：实现一个支持变量的简单 REPL

为了让读者能够亲手体验这一切，我们用 Python 实现一个完整的、带运行时环境的 REPL（交互式解释器）。

这个实现包含了：
1. **持久化的运行环境（Environment）**，确保在 REPL 中输入的变量能在下一次输入中被使用。
2. **简单的 LL(2) 前瞻**，避免了复杂的回溯，使得赋值和表达式能够被清晰分流。

```python
import sys

# ==================== 1. 词法分析 (Lexer) ====================
class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value
    def __repr__(self):
        return f"{self.type}({self.value})"

def tokenize(code: str):
    tokens = []
    i = 0
    while i < len(code):
        if code[i].isspace():
            i += 1
            continue
        if code[i:i+3] == "int" and (i+3 >= len(code) or not code[i+3].isalnum()):
            tokens.append(Token("INT", "int"))
            i += 3
            continue
        if code[i].isalpha():
            start = i
            while i < len(code) and code[i].isalnum(): i += 1
            tokens.append(Token("IDENTIFIER", code[start:i]))
            continue
        if code[i].isdigit():
            start = i
            while i < len(code) and code[i].isdigit(): i += 1
            tokens.append(Token("NUMBER", int(code[start:i])))
            continue
        if code[i] in "+-*/=;()":
            tokens.append(Token(code[i], code[i]))
            i += 1
            continue
        raise SyntaxError(f"未知字符: {code[i]}")
    tokens.append(Token("EOF", ""))
    return tokens

# ==================== 2. AST 节点设计 ====================
class VarDeclNode:
    def __init__(self, name, initializer):
        self.name = name
        self.initializer = initializer

class AssignNode:
    def __init__(self, name, value_expr):
        self.name = name
        self.value_expr = value_expr

class VarRefNode:
    def __init__(self, name):
        self.name = name

class LiteralNode:
    def __init__(self, value):
        self.value = value

class BinaryOpNode:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

# ==================== 3. 语法分析器 (Parser) ====================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        if self.pos + offset >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.pos + offset]

    def match(self, *types):
        if self.peek().type in types:
            self.pos += 1
            return True
        return False

    def consume(self, type, err_msg):
        if self.match(type):
            return self.tokens[self.pos - 1]
        raise SyntaxError(f"语法错误: {err_msg}，实际读到 '{self.peek().value}'")

    def parse_statement(self):
        # 1. 解析 int 声明语句
        if self.match("INT"):
            # 一旦读到 'int'，进入提交点，任何不匹配都直接报错，不回溯
            name = self.consume("IDENTIFIER", "期待变量名").value
            initializer = None
            if self.match("="):
                initializer = self.parse_expression()
            self.consume(";", "声明语句缺少分号 ';'")
            return VarDeclNode(name, initializer)

        # 2. 用 LL(2) 前瞻区分 赋值语句 和 表达式语句
        if self.peek(0).type == "IDENTIFIER" and self.peek(1).type == "=":
            # 确定是赋值语句，进入提交点
            name = self.consume("IDENTIFIER", "").value
            self.consume("=", "")
            expr = self.parse_expression()
            self.consume(";", "赋值语句缺少分号 ';'")
            return AssignNode(name, expr)

        # 3. 默认作为表达式语句处理
        expr = self.parse_expression()
        self.consume(";", "表达式语句缺少分号 ';'")
        return expr

    def parse_expression(self):
        left = self.parse_term()
        while self.match("+", "-"):
            op = self.tokens[self.pos - 1].type
            right = self.parse_term()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_term(self):
        left = self.parse_primary()
        while self.match("*", "/"):
            op = self.tokens[self.pos - 1].type
            right = self.parse_primary()
            left = BinaryOpNode(op, left, right)
        return left

    def parse_primary(self):
        if self.match("NUMBER"):
            return LiteralNode(self.tokens[self.pos - 1].value)
        if self.match("IDENTIFIER"):
            return VarRefNode(self.tokens[self.pos - 1].value)
        if self.match("("):
            expr = self.parse_expression()
            self.consume(")", "期待右括号 ')'")
            return expr
        raise SyntaxError(f"期待表达式，读到: {self.peek().value}")

# ==================== 4. 解释器与运行环境 ====================
class Environment:
    def __init__(self):
        self.variables = {}

    def define(self, name, value):
        self.variables[name] = value

    def assign(self, name, value):
        if name in self.variables:
            self.variables[name] = value
        else:
            raise NameError(f"未声明的变量: '{name}'")

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        raise NameError(f"未初始化的变量: '{name}'")

def evaluate(node, env):
    if isinstance(node, LiteralNode):
        return node.value
    if isinstance(node, VarRefNode):
        return env.get(node.name)
    if isinstance(node, BinaryOpNode):
        l = evaluate(node.left, env)
        r = evaluate(node.right, env)
        if node.op == '+': return l + r
        if node.op == '-': return l - r
        if node.op == '*': return l * r
        if node.op == '/': return l / r
    if isinstance(node, VarDeclNode):
        val = evaluate(node.initializer, env) if node.initializer else None
        env.define(node.name, val)
        return f"Defined {node.name} = {val}"
    if isinstance(node, AssignNode):
        val = evaluate(node.value_expr, env)
        env.assign(node.name, val)
        return f"{node.name} = {val}"
    return None

# ==================== 5. 实现 REPL (交互式解析器) ====================
def repl():
    print("简单脚本语言 REPL (输入 'exit' 退出)")
    env = Environment()
    while True:
        try:
            line = input(">> ").strip()
            if not line: continue
            if line == "exit": break

            # 词法分析
            tokens = tokenize(line)
            # 语法分析
            parser = Parser(tokens)
            stmt = parser.parse_statement()
            # 求值执行
            result = evaluate(stmt, env)
            
            # 如果是单纯的表达式语句，也把结果打印出来
            if result is None and not isinstance(stmt, (VarDeclNode, AssignNode)):
                result = evaluate(stmt, env)
            
            if result is not None:
                print(result)

        except (SyntaxError, NameError) as e:
            print(f"错误: {e}", file=sys.stderr)
        except Exception as e:
            print(f"系统错误: {e}", file=sys.stderr)

if __name__ == "__main__":
    repl()
```

### 这个 REPL 的精妙测试样例

你可以直接运行这段 Python 代码，并在交互界面中输入以下内容验证：

```text
>> int a = 10;
Defined a = 10
>> int b = a * 2 + 5;
Defined b = 25
>> b = b + 5;
b = 30
>> b;
30
>> int c = ;
错误: 语法错误: 期待表达式，实际读到 ';'  <-- 精准识别语法错误，未触发回溯
>> d = 5;
错误: 未声明的变量: 'd'                  <-- 运行时作用域检查
```
