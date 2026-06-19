"""Starter problem bank — first-year problems, solvable in Python *or* Java.

Test cases are language-agnostic (stdin -> stdout), so each problem ships with
a Python stub (`starter_code`) and a Java stub (`java_starter`); the student
picks a language in the editor. Outputs avoid floats to keep grading
deterministic across languages.
"""

# Reusable Java skeletons (kept short; students fill the TODO).
_J_INT = (
    "import java.util.Scanner;\n\n"
    "public class Main {\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        int n = sc.nextInt();\n"
    "        // TODO: solve and print the answer\n"
    "    }\n"
    "}\n"
)
_J_LINE = (
    "import java.util.Scanner;\n\n"
    "public class Main {\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        String s = sc.nextLine();\n"
    "        // TODO: solve and print the answer\n"
    "    }\n"
    "}\n"
)
_J_TWO_INTS = (
    "import java.util.Scanner;\n\n"
    "public class Main {\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        int a = sc.nextInt(), b = sc.nextInt();\n"
    "        // TODO: solve and print the answer\n"
    "    }\n"
    "}\n"
)
_J_LIST = (
    "import java.util.Scanner;\n\n"
    "public class Main {\n"
    "    public static void main(String[] args) {\n"
    "        Scanner sc = new Scanner(System.in);\n"
    "        int n = sc.nextInt();\n"
    "        int[] nums = new int[n];\n"
    "        for (int i = 0; i < n; i++) nums[i] = sc.nextInt();\n"
    "        // TODO: solve and print the answer\n"
    "    }\n"
    "}\n"
)

_ALL = ["python", "java"]


def _fizzbuzz(n):
    out = []
    for i in range(1, n + 1):
        if i % 15 == 0:
            out.append("FizzBuzz")
        elif i % 3 == 0:
            out.append("Fizz")
        elif i % 5 == 0:
            out.append("Buzz")
        else:
            out.append(str(i))
    return "\n".join(out)


def _table(n):
    return "\n".join(f"{n} x {i} = {n * i}" for i in range(1, 11))


PROBLEMS = [
    {
        "slug": "sum-to-n", "title": "Sum from 1 to N", "concept": "loops",
        "difficulty": "easy", "languages": _ALL,
        "description": (
            "Read an integer N. Print the sum of all integers from 1 to N, "
            "inclusive.\n\nExample: N = 5 -> 15 (1+2+3+4+5)."
        ),
        "starter_code": "n = int(input())\n# TODO: print the sum of 1..n (inclusive)\n",
        "java_starter": _J_INT,
        "test_cases": [
            {"input": "5\n", "expected_output": "15", "is_hidden": False},
            {"input": "1\n", "expected_output": "1", "is_hidden": False},
            {"input": "100\n", "expected_output": "5050", "is_hidden": True},
        ],
    },
    {
        "slug": "factorial", "title": "Factorial", "concept": "recursion",
        "difficulty": "easy", "languages": _ALL,
        "description": "Read a non-negative integer N. Print N! (0! = 1).\n\nExample: 5 -> 120.",
        "starter_code": (
            "def fact(n):\n    # TODO: implement (remember the base case)\n    pass\n\n"
            "n = int(input())\nprint(fact(n))\n"
        ),
        "java_starter": (
            "import java.util.Scanner;\n\n"
            "public class Main {\n"
            "    static long fact(int n) {\n"
            "        // TODO: implement (remember the base case)\n"
            "        return 0;\n"
            "    }\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        System.out.println(fact(sc.nextInt()));\n"
            "    }\n"
            "}\n"
        ),
        "test_cases": [
            {"input": "5\n", "expected_output": "120", "is_hidden": False},
            {"input": "0\n", "expected_output": "1", "is_hidden": False},
            {"input": "7\n", "expected_output": "5040", "is_hidden": True},
        ],
    },
    {
        "slug": "reverse-string", "title": "Reverse a String", "concept": "strings",
        "difficulty": "easy", "languages": _ALL,
        "description": "Read a line of text. Print it reversed.\n\nExample: 'hello' -> 'olleh'.",
        "starter_code": "s = input()\n# TODO: print s reversed\n",
        "java_starter": _J_LINE,
        "test_cases": [
            {"input": "hello\n", "expected_output": "olleh", "is_hidden": False},
            {"input": "DebugMyMind\n", "expected_output": "dniMyMgubeD", "is_hidden": True},
        ],
    },
    {
        "slug": "count-vowels", "title": "Count the Vowels", "concept": "strings",
        "difficulty": "easy", "languages": _ALL,
        "description": (
            "Read a line of text. Print how many vowels (a, e, i, o, u, "
            "case-insensitive) it contains.\n\nExample: 'Apple' -> 2."
        ),
        "starter_code": "s = input()\n# TODO: count and print the number of vowels\n",
        "java_starter": _J_LINE,
        "test_cases": [
            {"input": "Apple\n", "expected_output": "2", "is_hidden": False},
            {"input": "rhythm\n", "expected_output": "0", "is_hidden": False},
            {"input": "EDUCATION\n", "expected_output": "5", "is_hidden": True},
        ],
    },
    {
        "slug": "max-in-list", "title": "Maximum of a List", "concept": "lists",
        "difficulty": "easy", "languages": _ALL,
        "description": (
            "The first line is N. The second line has N space-separated integers. "
            "Print the largest.\n\nDo not use a built-in max — practice the loop."
        ),
        "starter_code": (
            "n = int(input())\nnums = list(map(int, input().split()))\n"
            "# TODO: find and print the largest value\n"
        ),
        "java_starter": _J_LIST,
        "test_cases": [
            {"input": "5\n3 9 1 7 4\n", "expected_output": "9", "is_hidden": False},
            {"input": "3\n-5 -2 -9\n", "expected_output": "-2", "is_hidden": False},
            {"input": "1\n42\n", "expected_output": "42", "is_hidden": True},
        ],
    },
    {
        "slug": "fizzbuzz", "title": "FizzBuzz", "concept": "conditionals",
        "difficulty": "easy", "languages": _ALL,
        "description": (
            "Read N. Print 1..N, one per line, but 'Fizz' for multiples of 3, "
            "'Buzz' for multiples of 5, and 'FizzBuzz' for multiples of both."
        ),
        "starter_code": "n = int(input())\n# TODO: print the FizzBuzz sequence, one item per line\n",
        "java_starter": _J_INT,
        "test_cases": [
            {"input": "5\n", "expected_output": _fizzbuzz(5), "is_hidden": False},
            {"input": "15\n", "expected_output": _fizzbuzz(15), "is_hidden": True},
        ],
    },
    {
        "slug": "is-prime", "title": "Prime Check", "concept": "loops",
        "difficulty": "medium", "languages": _ALL,
        "description": "Read an integer N (>= 2). Print 'YES' if it is prime, else 'NO'.",
        "starter_code": "n = int(input())\n# TODO: print YES if n is prime, else NO\n",
        "java_starter": _J_INT,
        "test_cases": [
            {"input": "7\n", "expected_output": "YES", "is_hidden": False},
            {"input": "9\n", "expected_output": "NO", "is_hidden": False},
            {"input": "2\n", "expected_output": "YES", "is_hidden": True},
            {"input": "97\n", "expected_output": "YES", "is_hidden": True},
        ],
    },
    {
        "slug": "fibonacci", "title": "Nth Fibonacci", "concept": "recursion",
        "difficulty": "medium", "languages": _ALL,
        "description": (
            "Read N (N >= 0). Print the Nth Fibonacci number, where fib(0) = 0, "
            "fib(1) = 1, fib(n) = fib(n-1) + fib(n-2)."
        ),
        "starter_code": (
            "def fib(n):\n    # TODO: implement (mind the two base cases)\n    pass\n\n"
            "n = int(input())\nprint(fib(n))\n"
        ),
        "java_starter": (
            "import java.util.Scanner;\n\n"
            "public class Main {\n"
            "    static int fib(int n) {\n"
            "        // TODO: implement (mind the two base cases)\n"
            "        return 0;\n"
            "    }\n"
            "    public static void main(String[] args) {\n"
            "        Scanner sc = new Scanner(System.in);\n"
            "        System.out.println(fib(sc.nextInt()));\n"
            "    }\n"
            "}\n"
        ),
        "test_cases": [
            {"input": "0\n", "expected_output": "0", "is_hidden": False},
            {"input": "1\n", "expected_output": "1", "is_hidden": False},
            {"input": "10\n", "expected_output": "55", "is_hidden": True},
        ],
    },
    {
        "slug": "even-or-odd", "title": "Even or Odd", "concept": "conditionals",
        "difficulty": "easy", "languages": _ALL,
        "description": "Read an integer N. Print 'Even' if it is even, else 'Odd'.",
        "starter_code": "n = int(input())\n# TODO: print Even or Odd\n",
        "java_starter": _J_INT,
        "test_cases": [
            {"input": "4\n", "expected_output": "Even", "is_hidden": False},
            {"input": "7\n", "expected_output": "Odd", "is_hidden": False},
            {"input": "0\n", "expected_output": "Even", "is_hidden": True},
        ],
    },
    {
        "slug": "sum-of-digits", "title": "Sum of Digits", "concept": "loops",
        "difficulty": "easy", "languages": _ALL,
        "description": "Read a non-negative integer N. Print the sum of its digits.\n\nExample: 1234 -> 10.",
        "starter_code": "n = int(input())\n# TODO: print the sum of the digits of n\n",
        "java_starter": _J_INT,
        "test_cases": [
            {"input": "1234\n", "expected_output": "10", "is_hidden": False},
            {"input": "9\n", "expected_output": "9", "is_hidden": False},
            {"input": "99999\n", "expected_output": "45", "is_hidden": True},
        ],
    },
    {
        "slug": "palindrome-check", "title": "Palindrome Check", "concept": "strings",
        "difficulty": "easy", "languages": _ALL,
        "description": "Read a line. Print 'YES' if it reads the same forwards and backwards, else 'NO'.",
        "starter_code": "s = input()\n# TODO: print YES if s is a palindrome, else NO\n",
        "java_starter": _J_LINE,
        "test_cases": [
            {"input": "racecar\n", "expected_output": "YES", "is_hidden": False},
            {"input": "hello\n", "expected_output": "NO", "is_hidden": False},
            {"input": "level\n", "expected_output": "YES", "is_hidden": True},
        ],
    },
    {
        "slug": "gcd", "title": "Greatest Common Divisor", "concept": "recursion",
        "difficulty": "medium", "languages": _ALL,
        "description": (
            "Read two integers A and B on one line (space-separated). Print their "
            "greatest common divisor.\n\nExample: 12 18 -> 6."
        ),
        "starter_code": (
            "a, b = map(int, input().split())\n# TODO: print gcd(a, b)\n"
        ),
        "java_starter": _J_TWO_INTS,
        "test_cases": [
            {"input": "12 18\n", "expected_output": "6", "is_hidden": False},
            {"input": "17 5\n", "expected_output": "1", "is_hidden": False},
            {"input": "100 75\n", "expected_output": "25", "is_hidden": True},
        ],
    },
    {
        "slug": "power", "title": "Power (base^exp)", "concept": "recursion",
        "difficulty": "medium", "languages": _ALL,
        "description": (
            "Read two integers BASE and EXP (EXP >= 0) on one line. Print BASE "
            "raised to EXP.\n\nExample: 2 10 -> 1024."
        ),
        "starter_code": "base, exp = map(int, input().split())\n# TODO: print base ** exp\n",
        "java_starter": _J_TWO_INTS,
        "test_cases": [
            {"input": "2 10\n", "expected_output": "1024", "is_hidden": False},
            {"input": "5 0\n", "expected_output": "1", "is_hidden": False},
            {"input": "3 4\n", "expected_output": "81", "is_hidden": True},
        ],
    },
    {
        "slug": "count-evens", "title": "Count Even Numbers", "concept": "lists",
        "difficulty": "easy", "languages": _ALL,
        "description": (
            "First line N, second line N space-separated integers. Print how many "
            "of them are even."
        ),
        "starter_code": (
            "n = int(input())\nnums = list(map(int, input().split()))\n"
            "# TODO: count and print how many are even\n"
        ),
        "java_starter": _J_LIST,
        "test_cases": [
            {"input": "5\n1 2 3 4 6\n", "expected_output": "3", "is_hidden": False},
            {"input": "3\n1 3 5\n", "expected_output": "0", "is_hidden": False},
            {"input": "4\n2 4 6 8\n", "expected_output": "4", "is_hidden": True},
        ],
    },
    {
        "slug": "second-largest", "title": "Second Largest", "concept": "lists",
        "difficulty": "medium", "languages": _ALL,
        "description": (
            "First line N (N >= 2), second line N space-separated distinct "
            "integers. Print the second largest."
        ),
        "starter_code": (
            "n = int(input())\nnums = list(map(int, input().split()))\n"
            "# TODO: print the second largest value\n"
        ),
        "java_starter": _J_LIST,
        "test_cases": [
            {"input": "5\n3 9 1 7 4\n", "expected_output": "7", "is_hidden": False},
            {"input": "4\n10 5 8 2\n", "expected_output": "8", "is_hidden": False},
            {"input": "3\n1 2 3\n", "expected_output": "2", "is_hidden": True},
        ],
    },
    {
        "slug": "leap-year", "title": "Leap Year", "concept": "conditionals",
        "difficulty": "easy", "languages": _ALL,
        "description": (
            "Read a year. Print 'YES' if it is a leap year, else 'NO'. (Divisible "
            "by 4, except centuries which must be divisible by 400.)"
        ),
        "starter_code": "year = int(input())\n# TODO: print YES if leap year, else NO\n",
        "java_starter": _J_INT,
        "test_cases": [
            {"input": "2000\n", "expected_output": "YES", "is_hidden": False},
            {"input": "1900\n", "expected_output": "NO", "is_hidden": False},
            {"input": "2024\n", "expected_output": "YES", "is_hidden": True},
            {"input": "2023\n", "expected_output": "NO", "is_hidden": True},
        ],
    },
    {
        "slug": "reverse-number", "title": "Reverse a Number", "concept": "loops",
        "difficulty": "easy", "languages": _ALL,
        "description": (
            "Read a non-negative integer N. Print its digits reversed, as a number "
            "(no leading zeros).\n\nExample: 1234 -> 4321, 1000 -> 1."
        ),
        "starter_code": "n = int(input())\n# TODO: print the digits of n reversed\n",
        "java_starter": _J_INT,
        "test_cases": [
            {"input": "1234\n", "expected_output": "4321", "is_hidden": False},
            {"input": "1000\n", "expected_output": "1", "is_hidden": False},
            {"input": "9\n", "expected_output": "9", "is_hidden": True},
        ],
    },
    {
        "slug": "multiplication-table", "title": "Multiplication Table", "concept": "loops",
        "difficulty": "easy", "languages": _ALL,
        "description": (
            "Read N. Print N's multiplication table from 1 to 10, one line each, "
            "formatted exactly as 'N x i = result'.\n\nExample line: 3 x 4 = 12."
        ),
        "starter_code": "n = int(input())\n# TODO: print the table, e.g. 'n x 1 = ...'\n",
        "java_starter": _J_INT,
        "test_cases": [
            {"input": "3\n", "expected_output": _table(3), "is_hidden": False},
            {"input": "5\n", "expected_output": _table(5), "is_hidden": True},
        ],
    },
    {
        "slug": "count-words", "title": "Count Words", "concept": "strings",
        "difficulty": "easy", "languages": _ALL,
        "description": (
            "Read a line of words separated by single spaces. Print how many "
            "words it contains.\n\nExample: 'hello world foo' -> 3."
        ),
        "starter_code": "s = input()\n# TODO: print the number of words\n",
        "java_starter": _J_LINE,
        "test_cases": [
            {"input": "hello world foo\n", "expected_output": "3", "is_hidden": False},
            {"input": "single\n", "expected_output": "1", "is_hidden": False},
            {"input": "a b c d e\n", "expected_output": "5", "is_hidden": True},
        ],
    },
    {
        "slug": "armstrong-number", "title": "Armstrong Number", "concept": "loops",
        "difficulty": "hard", "languages": _ALL,
        "description": (
            "Read N. Print 'YES' if N is an Armstrong number (the sum of each "
            "digit raised to the power of the number of digits equals N), else "
            "'NO'.\n\nExample: 153 = 1^3 + 5^3 + 3^3 -> YES."
        ),
        "starter_code": "n = int(input())\n# TODO: print YES if n is an Armstrong number, else NO\n",
        "java_starter": _J_INT,
        "test_cases": [
            {"input": "153\n", "expected_output": "YES", "is_hidden": False},
            {"input": "123\n", "expected_output": "NO", "is_hidden": False},
            {"input": "9474\n", "expected_output": "YES", "is_hidden": True},
            {"input": "370\n", "expected_output": "YES", "is_hidden": True},
        ],
    },
]
