"""Code generator: AST -> stack-based bytecode.

Each function compiles to a flat list of instructions. Jump targets are
patched once the destination offset is known (the classic backpatching
dance every compiler writer meets).

Instruction set:
    PUSH n          push a literal
    LOAD name       push a local variable
    STORE name      pop into a local variable
    ADD SUB MUL DIV MOD
    EQ NE LT LE GT GE
    AND OR NOT NEG
    JMP addr        unconditional jump
    JZ addr         pop, jump if zero
    CALL name argc  call a function, args already pushed
    RET             return top of stack to the caller
    PRINT           pop and print
    POP             discard top of stack
    HALT            stop the machine
"""

import parser as ast


class CompileError(Exception):
    pass


BINOPS = {
    "+": "ADD", "-": "SUB", "*": "MUL", "/": "DIV", "%": "MOD",
    "==": "EQ", "!=": "NE", "<": "LT", "<=": "LE", ">": "GT", ">=": "GE",
    "&&": "AND", "||": "OR",
}


class FunctionCode:
    def __init__(self, name, params):
        self.name = name
        self.params = params
        self.code = []

    def emit(self, op, arg=None):
        self.code.append((op, arg))
        return len(self.code) - 1

    def patch(self, pos, arg):
        op, _ = self.code[pos]
        self.code[pos] = (op, arg)


class Compiler:
    def __init__(self):
        self.functions = {}

    def compile(self, program):
        for fn in program.functions:
            if fn.name in self.functions:
                raise CompileError(f"function {fn.name} defined twice")
            code = FunctionCode(fn.name, fn.params)
            self.functions[fn.name] = code
            self._block(code, fn.body)
            code.emit("PUSH", 0)       # implicit return 0
            code.emit("RET")
        if "main" not in self.functions:
            raise CompileError("program has no main function")
        return self.functions

    # -- statements -----------------------------------------------------
    def _block(self, code, block):
        for stmt in block.stmts:
            self._stmt(code, stmt)

    def _stmt(self, code, stmt):
        if isinstance(stmt, ast.Block):
            self._block(code, stmt)
        elif isinstance(stmt, ast.Decl):
            if stmt.init is not None:
                self._expr(code, stmt.init)
            else:
                code.emit("PUSH", 0)
            code.emit("STORE", stmt.name)
        elif isinstance(stmt, ast.Assign):
            self._expr(code, stmt.expr)
            code.emit("STORE", stmt.name)
        elif isinstance(stmt, ast.If):
            self._expr(code, stmt.cond)
            jz = code.emit("JZ", None)
            self._stmt(code, stmt.then)
            if stmt.otherwise is not None:
                jmp = code.emit("JMP", None)
                code.patch(jz, len(code.code))
                self._stmt(code, stmt.otherwise)
                code.patch(jmp, len(code.code))
            else:
                code.patch(jz, len(code.code))
        elif isinstance(stmt, ast.While):
            start = len(code.code)
            self._expr(code, stmt.cond)
            jz = code.emit("JZ", None)
            self._stmt(code, stmt.body)
            code.emit("JMP", start)
            code.patch(jz, len(code.code))
        elif isinstance(stmt, ast.Return):
            self._expr(code, stmt.expr)
            code.emit("RET")
        elif isinstance(stmt, ast.Print):
            self._expr(code, stmt.expr)
            code.emit("PRINT")
        elif isinstance(stmt, ast.ExprStmt):
            self._expr(code, stmt.expr)
            code.emit("POP")
        else:
            raise CompileError(f"cannot compile statement {stmt!r}")

    # -- expressions ------------------------------------------------------
    def _expr(self, code, expr):
        if isinstance(expr, ast.Num):
            code.emit("PUSH", expr.value)
        elif isinstance(expr, ast.Var):
            code.emit("LOAD", expr.name)
        elif isinstance(expr, ast.Call):
            # Forward references are allowed; the VM raises a clear
            # error at call time if the function does not exist.
            for arg in expr.args:
                self._expr(code, arg)
            code.emit("CALL", (expr.name, len(expr.args)))
        elif isinstance(expr, ast.BinOp):
            self._expr(code, expr.left)
            self._expr(code, expr.right)
            code.emit(BINOPS[expr.op])
        elif isinstance(expr, ast.UnaryOp):
            self._expr(code, expr.operand)
            code.emit("NEG" if expr.op == "-" else "NOT")
        else:
            raise CompileError(f"cannot compile expression {expr!r}")


def compile_program(program):
    return Compiler().compile(program)


def disassemble(functions):
    lines = []
    for name, fn in functions.items():
        lines.append(f"== {name}({', '.join(fn.params)}) ==")
        for i, (op, arg) in enumerate(fn.code):
            lines.append(f"  {i:3} {op}" + ("" if arg is None else f" {arg}"))
    return "\n".join(lines)
