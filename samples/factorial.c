// Factorial, two ways: recursive and iterative.

int fact(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * fact(n - 1);
}

int fact_iter(int n) {
    int result = 1;
    int i = 2;
    while (i <= n) {
        result = result * i;
        i = i + 1;
    }
    return result;
}

int main() {
    print fact(5);
    print fact(10);
    print fact_iter(5);
    print fact_iter(10);
    return 0;
}
