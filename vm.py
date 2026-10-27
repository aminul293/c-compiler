"""A tiny stack-based virtual machine for TinyC bytecode.

Each call frame has its own operand stack and locals dict, so
recursion just works: factorial calling itself gets a fresh frame
every time. The machine runs until main returns.
"""


class VMError(Exception):
    pass


class Frame:
    def __init__(self, fn, args):
        self.fn = fn
        self.ip = 0
        self.stack = []
        self.locals = dict(zip(fn.params, args))


class VM:
    def __init__(self, functions, out=None):
        self.functions = functions
        self.out = out if out is not None else print

    def run(self):
        main = self.functions["main"]
        frames = [Frame(main, [])]
        while frames:
            frame = frames[-1]
            if frame.ip >= len(frame.fn.code):
                frames.pop()
                if frames:
                    frames[-1].stack.append(0)
                break
            op, arg = frame.fn.code[frame.ip]
            frame.ip += 1
            stack = frame.stack

            if op == "PUSH":
                stack.append(arg)
            elif op == "LOAD":
                if arg not in frame.locals:
                    raise VMError(f"undefined variable {arg!r} in {frame.fn.name}")
                stack.append(frame.locals[arg])
            elif op == "STORE":
                frame.locals[arg] = stack.pop()
            elif op in ("ADD", "SUB", "MUL", "DIV", "MOD",
                        "EQ", "NE", "LT", "LE", "GT", "GE", "AND", "OR"):
                b, a = stack.pop(), stack.pop()
                stack.append(self._binop(op, a, b))
            elif op == "NOT":
                stack.append(0 if stack.pop() else 1)
            elif op == "NEG":
                stack.append(-stack.pop())
            elif op == "JMP":
                frame.ip = arg
            elif op == "JZ":
                if stack.pop() == 0:
                    frame.ip = arg
            elif op == "CALL":
                name, argc = arg
                if name not in self.functions:
                    raise VMError(f"call to undefined function {name!r}")
                args = [stack.pop() for _ in range(argc)][::-1]
                frames.append(Frame(self.functions[name], args))
            elif op == "RET":
                value = stack.pop() if stack else 0
                frames.pop()
                if frames:
                    frames[-1].stack.append(value)
            elif op == "PRINT":
                self.out(stack.pop())
            elif op == "POP":
                stack.pop()
            elif op == "HALT":
                return
            else:
                raise VMError(f"unknown opcode {op!r}")

    @staticmethod
    def _binop(op, a, b):
        if op == "ADD":
            return a + b
        if op == "SUB":
            return a - b
        if op == "MUL":
            return a * b
        if op == "DIV":
            if b == 0:
                raise VMError("division by zero")
            q = abs(a) // abs(b)
            return q if (a < 0) == (b < 0) else -q   # C truncates toward zero
        if op == "MOD":
            if b == 0:
                raise VMError("modulo by zero")
            return a - VM._binop("DIV", a, b) * b
        if op == "EQ":
            return 1 if a == b else 0
        if op == "NE":
            return 1 if a != b else 0
        if op == "LT":
            return 1 if a < b else 0
        if op == "LE":
            return 1 if a <= b else 0
        if op == "GT":
            return 1 if a > b else 0
        if op == "GE":
            return 1 if a >= b else 0
        if op == "AND":
            return 1 if (a and b) else 0
        if op == "OR":
            return 1 if (a or b) else 0
        raise VMError(f"unknown binop {op!r}")
