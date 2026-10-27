"""Parser for TinyC: tokens -> AST.

Grammar (one function per rule, classic recursive descent):

    program  := funcdef*
    funcdef  := 'int' IDENT '(' params ')' block
    block    := '{' stmt* '}'
    stmt     := 'int' IDENT ('=' expr)? ';'
              | 'if' '(' expr ')' stmt ('else' stmt)?
              | 'while' '(' expr ')' stmt
              | 'return' expr ';'
              | 'print' expr ';'
              | block
              | IDENT '=' expr ';'
              | expr ';'
    expr     := or_expr
    or/and/equality/comparison/additive/multiplicative: binary chains
    unary    := ('-' | '!') unary | primary
    primary  := NUM | IDENT | IDENT '(' args ')' | '(' expr ')'
"""

from dataclasses import dataclass, field


class ParseError(Exception):
    pass


# ------------------------------------------------------------ AST nodes

@dataclass
class Program:
    functions: list

@dataclass
class FuncDef:
    name: str
    params: list
    body: object

@dataclass
class Block:
    stmts: list

@dataclass
class Decl:
    name: str
    init: object = None

@dataclass
class Assign:
    name: str
    expr: object

@dataclass
class If:
    cond: object
    then: object
    otherwise: object = None

@dataclass
class While:
    cond: object
    body: object

@dataclass
class Return:
    expr: object

@dataclass
class Print:
    expr: object

@dataclass
class ExprStmt:
    expr: object

@dataclass
class Num:
    value: int

@dataclass
class Var:
    name: str

@dataclass
class Call:
    name: str
    args: list = field(default_factory=list)

@dataclass
class BinOp:
    op: str
    left: object
    right: object

@dataclass
class UnaryOp:
    op: str
    operand: object


# ------------------------------------------------------------ parser

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.i = 0

    def peek(self, ahead=0):
        return self.tokens[self.i + ahead]

    def next(self):
        tok = self.tokens[self.i]
        self.i += 1
        return tok

    def expect(self, value):
        tok = self.next()
        if tok.value != value:
            raise ParseError(f"line {tok.line}: expected {value!r}, got {tok.value!r}")
        return tok

    def accept(self, value):
        if self.peek().value == value:
            self.i += 1
            return True
        return False

    def ident(self):
        tok = self.next()
        if tok.kind != "IDENT":
            raise ParseError(f"line {tok.line}: expected a name, got {tok.value!r}")
        return tok.value

    # -- program level -------------------------------------------------
    def parse_program(self):
        functions = []
        while self.peek().kind != "EOF":
            functions.append(self.parse_funcdef())
        if not functions:
            raise ParseError("empty program")
        return Program(functions)

    def parse_funcdef(self):
        self.expect("int")
        name = self.ident()
        self.expect("(")
        params = []
        if self.peek().value != ")":
            self.expect("int")
            params.append(self.ident())
            while self.accept(","):
                self.expect("int")
                params.append(self.ident())
        self.expect(")")
        return FuncDef(name, params, self.parse_block())

    def parse_block(self):
        self.expect("{")
        stmts = []
        while self.peek().value != "}":
            stmts.append(self.parse_stmt())
        self.expect("}")
        return Block(stmts)

    # -- statements ------------------------------------------------------
    def parse_stmt(self):
        tok = self.peek()
        if tok.value == "{":
            return self.parse_block()
        if tok.value == "int":
            self.next()
            name = self.ident()
            init = None
            if self.accept("="):
                init = self.parse_expr()
            self.expect(";")
            return Decl(name, init)
        if tok.value == "if":
            self.next()
            self.expect("(")
            cond = self.parse_expr()
            self.expect(")")
            then = self.parse_stmt()
            otherwise = None
            if self.peek().value == "else":
                self.next()
                otherwise = self.parse_stmt()
            return If(cond, then, otherwise)
        if tok.value == "while":
            self.next()
            self.expect("(")
            cond = self.parse_expr()
            self.expect(")")
            return While(cond, self.parse_stmt())
        if tok.value == "return":
            self.next()
            expr = self.parse_expr()
            self.expect(";")
            return Return(expr)
        if tok.value == "print":
            self.next()
            expr = self.parse_expr()
            self.expect(";")
            return Print(expr)
        if tok.kind == "IDENT" and self.peek(1).value == "=":
            name = self.next().value
            self.next()
            expr = self.parse_expr()
            self.expect(";")
            return Assign(name, expr)
        expr = self.parse_expr()
        self.expect(";")
        return ExprStmt(expr)

    # -- expressions ------------------------------------------------------
    def parse_expr(self):
        return self._binary(self.parse_and, ("||",))

    def parse_and(self):
        return self._binary(self.parse_equality, ("&&",))

    def parse_equality(self):
        return self._binary(self.parse_comparison, ("==", "!="))

    def parse_comparison(self):
        return self._binary(self.parse_additive, ("<", "<=", ">", ">="))

    def parse_additive(self):
        return self._binary(self.parse_term, ("+", "-"))

    def parse_term(self):
        return self._binary(self.parse_unary, ("*", "/", "%"))

    def _binary(self, sub, ops):
        left = sub()
        while self.peek().value in ops:
            op = self.next().value
            left = BinOp(op, left, sub())
        return left

    def parse_unary(self):
        tok = self.peek()
        if tok.value in ("-", "!"):
            self.next()
            return UnaryOp(tok.value, self.parse_unary())
        return self.parse_primary()

    def parse_primary(self):
        tok = self.next()
        if tok.kind == "NUM":
            return Num(tok.value)
        if tok.value == "(":
            expr = self.parse_expr()
            self.expect(")")
            return expr
        if tok.kind == "IDENT":
            if self.accept("("):
                args = []
                if self.peek().value != ")":
                    args.append(self.parse_expr())
                    while self.accept(","):
                        args.append(self.parse_expr())
                self.expect(")")
                return Call(tok.value, args)
            return Var(tok.value)
        raise ParseError(f"line {tok.line}: unexpected token {tok.value!r}")


def parse(tokens):
    return Parser(tokens).parse_program()
