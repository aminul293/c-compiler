// FizzBuzz for 1..20, printing numbers only.
// (TinyC prints integers, so Fizz prints as 3 and Buzz as 5.)

int main() {
    int i = 1;
    while (i <= 20) {
        if (i % 15 == 0) {
            print 15;
        } else if (i % 3 == 0) {
            print 3;
        } else if (i % 5 == 0) {
            print 5;
        } else {
            print i;
        }
        i = i + 1;
    }
    return 0;
}
