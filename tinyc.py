"""TinyC driver: compile a .c file and run it on the VM.

    python tinyc.py samples/factorial.c
    python tinyc.py samples/fizzbuzz.c --dump   (also print the bytecode)
"""

import sys

import codegen
import lexer
import parser
from vm import VM


def compile_source(src):
    tokens = lexer.tokenize(src)
    program = parser.parse(tokens)
    return codegen.compile_program(program)


def run_source(src, out=None):
    functions = compile_source(src)
    VM(functions, out=out).run()


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print("usage: python tinyc.py <program.c> [--dump]")
        return 1
    with open(args[0]) as fh:
        src = fh.read()
    functions = compile_source(src)
    if "--dump" in sys.argv:
        print(codegen.disassemble(functions))
        print("== output ==")
    VM(functions).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
