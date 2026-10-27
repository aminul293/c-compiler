import pytest

import lexer
import parser
from tinyc import compile_source, run_source
from vm import VMError


def run(src):
    out = []
    run_source(src, out=out.append)
    return out


def test_lexer_tokens():
    toks = lexer.tokenize("int x = 42; // comment\nx = x + 1;")
    values = [t.value for t in toks]
    assert values == ["int", "x", "=", 42, ";", "x", "=", "x", "+", 1, ";", None]


def test_lexer_error_line():
    with pytest.raises(lexer.LexError):
        lexer.tokenize("int x = @;")


def test_parser_builds_ast():
    prog = parser.parse(lexer.tokenize("int main() { return 1 + 2 * 3; }"))
    fn = prog.functions[0]
    assert fn.name == "main"
    ret = fn.body.stmts[0]
    assert ret.expr.op == "+"
    assert ret.expr.right.op == "*"     # precedence: * binds tighter


def test_arithmetic_and_precedence():
    assert run("int main() { print 2 + 3 * 4; print (2 + 3) * 4; "
               "print 10 % 3; print 7 / 2; print -7 / 2; return 0; }") == \
        [14, 20, 1, 3, -3]


def test_variables_and_assignment():
    src = ("int main() { int x = 5; int y; y = x * 2; x = x + 1; "
           "print x; print y; return 0; }")
    assert run(src) == [6, 10]


def test_if_else_and_comparison():
    src = ("int main() { int x = 7; if (x > 10) { print 1; } "
           "else if (x > 5) { print 2; } else { print 3; } return 0; }")
    assert run(src) == [2]


def test_while_loop_sum():
    src = ("int main() { int i = 1; int sum = 0; while (i <= 100) { "
           "sum = sum + i; i = i + 1; } print sum; return 0; }")
    assert run(src) == [5050]


def test_recursion_factorial():
    src = ("int fact(int n) { if (n <= 1) { return 1; } "
           "return n * fact(n - 1); } "
           "int main() { print fact(10); return 0; }")
    assert run(src) == [3628800]


def test_logic_operators():
    src = ("int main() { print 1 && 0; print 1 || 0; print !0; "
           "print 3 == 3; print 3 != 3; return 0; }")
    assert run(src) == [0, 1, 1, 1, 0]


def test_sample_programs():
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "samples", "factorial.c")) as fh:
        assert run(fh.read()) == [120, 3628800, 120, 3628800]
    with open(os.path.join(here, "samples", "fibonacci.c")) as fh:
        assert run(fh.read()) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
    with open(os.path.join(here, "samples", "fizzbuzz.c")) as fh:
        assert run(fh.read()) == [1, 2, 3, 4, 5, 3, 7, 8, 3, 5,
                                  11, 3, 13, 14, 15, 16, 17, 3, 19, 5]


def test_undefined_variable_is_an_error():
    with pytest.raises(VMError):
        run("int main() { print missing; return 0; }")


def test_division_by_zero_is_an_error():
    with pytest.raises(VMError):
        run("int main() { print 1 / 0; return 0; }")


def test_missing_main_is_a_compile_error():
    with pytest.raises(Exception):
        compile_source("int f() { return 1; }")
