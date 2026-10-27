# c-compiler

A compiler for a small C-like language, written in Python, plus the
stack-based virtual machine that runs its output. Lexer, parser,
code generator, bytecode VM: the full pipeline, each stage small
enough to read in one sitting.

The language is called TinyC. It has integer variables, arithmetic,
comparisons, if/else, while loops, functions with parameters and
return values (recursion included), and a print statement.

## Run it

```bash
python tinyc.py samples/factorial.c
python tinyc.py samples/fibonacci.c
python tinyc.py samples/fizzbuzz.c
python tinyc.py samples/factorial.c --dump   # see the bytecode too
python -m pytest                             # test suite
```

## Example

```c
int fact(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * fact(n - 1);
}

int main() {
    print fact(10);
    return 0;
}
```

Output: `3628800`

## The pipeline

1. **Lexer** (lexer.py): source text to tokens, with line numbers and
   comment support. Numbers, names, keywords, operators.
2. **Parser** (parser.py): recursive descent, one method per grammar
   rule, producing an AST. Operator precedence falls out of the call
   chain: or, and, equality, comparison, additive, multiplicative,
   unary, primary.
3. **Code generator** (codegen.py): walks the AST and emits stack
   bytecode. if/while compile to conditional jumps whose targets are
   backpatched once the destination is known.
4. **VM** (vm.py): executes the bytecode. Every function call gets a
   fresh frame with its own operand stack and locals, which is what
   makes recursion work. Division follows C: it truncates toward zero,
   including for negatives, and division by zero is a clean VM error,
   not a Python traceback.

The instruction set is 20-odd opcodes: PUSH, LOAD, STORE, the
arithmetic and comparison ops, JMP, JZ, CALL, RET, PRINT, POP, HALT.
Run any sample with --dump to see real output.

## What it demonstrates

How a language actually gets from text to behavior: tokenizing,
parsing with precedence, compiling control flow to jumps, and running
a stack machine. These are the internals behind every interpreter and
compiler, compressed into a few hundred lines.

## Honest scope

Integers only, no strings (the fizzbuzz sample prints 3, 5, and 15 as
stand-ins for the words, and says so in its comments), no arrays, no
pointers, no type checking beyond the VM catching undefined names at
run time, and print takes a single expression. It is a teaching
compiler, complete for its little language, not a C replacement.
