// Fibonacci: print the first 12 numbers of the sequence.

int fib(int n) {
    if (n < 2) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}

int main() {
    int i = 0;
    while (i < 12) {
        print fib(i);
        i = i + 1;
    }
    return 0;
}
