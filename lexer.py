"""Lexer for TinyC, a small C-like language.

Turns source text into tokens: numbers, identifiers, keywords, and
operators. Tracks line numbers so error messages can point somewhere
useful.
"""

KEYWORDS = {"int", "if", "else", "while", "return", "print"}

TWO_CHAR_OPS = ("==", "!=", "<=", ">=", "&&", "||")
ONE_CHAR_OPS = set("+-*/%<>=!(){};,")
WHITESPACE = set(" \t\r\n")


class LexError(Exception):
    pass


class Token:
    def __init__(self, kind, value, line):
        self.kind = kind        # 'NUM', 'IDENT', 'KW', 'OP', 'EOF'
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.kind}, {self.value!r}, line {self.line})"


def tokenize(src):
    tokens = []
    i, line = 0, 1
    n = len(src)
    while i < n:
        ch = src[i]
        if ch in WHITESPACE:
            if ch == "\n":
                line += 1
            i += 1
            continue
        if src.startswith("//", i):
            while i < n and src[i] != "\n":
                i += 1
            continue
        if ch.isdigit():
            j = i
            while j < n and src[j].isdigit():
                j += 1
            tokens.append(Token("NUM", int(src[i:j]), line))
            i = j
            continue
        if ch.isalpha() or ch == "_":
            j = i
            while j < n and (src[j].isalnum() or src[j] == "_"):
                j += 1
            word = src[i:j]
            kind = "KW" if word in KEYWORDS else "IDENT"
            tokens.append(Token(kind, word, line))
            i = j
            continue
        two = src[i:i + 2]
        if two in TWO_CHAR_OPS:
            tokens.append(Token("OP", two, line))
            i += 2
            continue
        if ch in ONE_CHAR_OPS:
            tokens.append(Token("OP", ch, line))
            i += 1
            continue
        raise LexError(f"line {line}: unexpected character {ch!r}")
    tokens.append(Token("EOF", None, line))
    return tokens
