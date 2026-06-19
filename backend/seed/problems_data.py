"""Starter problem bank — first-year Python problems by concept.

Each problem reads from stdin and prints the answer to stdout, so the Phase 2
sandboxed runner can grade it by comparing stdout to expected_output.
Target is 10-15 problems; this is the seed batch.
"""

PROBLEMS = [
    {
        "slug": "sum-to-n",
        "title": "Sum from 1 to N",
        "concept": "loops",
        "difficulty": "easy",
        "description": (
            "Read an integer N from input. Print the sum of all integers from "
            "1 to N, inclusive.\n\nExample: N = 5 -> 15 (1+2+3+4+5)."
        ),
        "starter_code": (
            "n = int(input())\n"
            "# TODO: print the sum of 1..n (inclusive)\n"
        ),
        "test_cases": [
            {"input": "5\n", "expected_output": "15", "is_hidden": False},
            {"input": "1\n", "expected_output": "1", "is_hidden": False},
            {"input": "100\n", "expected_output": "5050", "is_hidden": True},
        ],
    },
    {
        "slug": "factorial",
        "title": "Factorial",
        "concept": "recursion",
        "difficulty": "easy",
        "description": (
            "Read a non-negative integer N. Print N! (N factorial).\n"
            "Recall 0! = 1.\n\nExample: N = 5 -> 120."
        ),
        "starter_code": (
            "def fact(n):\n"
            "    # TODO: implement (remember the base case)\n"
            "    pass\n\n"
            "n = int(input())\n"
            "print(fact(n))\n"
        ),
        "test_cases": [
            {"input": "5\n", "expected_output": "120", "is_hidden": False},
            {"input": "0\n", "expected_output": "1", "is_hidden": False},
            {"input": "7\n", "expected_output": "5040", "is_hidden": True},
        ],
    },
    {
        "slug": "reverse-string",
        "title": "Reverse a String",
        "concept": "strings",
        "difficulty": "easy",
        "description": (
            "Read a line of text. Print it reversed.\n\n"
            "Example: 'hello' -> 'olleh'."
        ),
        "starter_code": (
            "s = input()\n"
            "# TODO: print s reversed\n"
        ),
        "test_cases": [
            {"input": "hello\n", "expected_output": "olleh", "is_hidden": False},
            {"input": "DebugMyMind\n", "expected_output": "dniMyMgubeD", "is_hidden": True},
        ],
    },
    {
        "slug": "count-vowels",
        "title": "Count the Vowels",
        "concept": "strings",
        "difficulty": "easy",
        "description": (
            "Read a line of text. Print how many vowels (a, e, i, o, u, "
            "case-insensitive) it contains.\n\nExample: 'Apple' -> 2."
        ),
        "starter_code": (
            "s = input()\n"
            "# TODO: count and print the number of vowels\n"
        ),
        "test_cases": [
            {"input": "Apple\n", "expected_output": "2", "is_hidden": False},
            {"input": "rhythm\n", "expected_output": "0", "is_hidden": False},
            {"input": "EDUCATION\n", "expected_output": "5", "is_hidden": True},
        ],
    },
    {
        "slug": "max-in-list",
        "title": "Maximum of a List",
        "concept": "lists",
        "difficulty": "easy",
        "description": (
            "The first line is N, the count of numbers. The second line has N "
            "space-separated integers. Print the largest.\n\n"
            "Do not use the built-in max() — practice the loop."
        ),
        "starter_code": (
            "n = int(input())\n"
            "nums = list(map(int, input().split()))\n"
            "# TODO: find and print the largest value\n"
        ),
        "test_cases": [
            {"input": "5\n3 9 1 7 4\n", "expected_output": "9", "is_hidden": False},
            {"input": "3\n-5 -2 -9\n", "expected_output": "-2", "is_hidden": False},
            {"input": "1\n42\n", "expected_output": "42", "is_hidden": True},
        ],
    },
    {
        "slug": "fizzbuzz",
        "title": "FizzBuzz",
        "concept": "conditionals",
        "difficulty": "easy",
        "description": (
            "Read N. Print numbers 1..N, one per line, but print 'Fizz' for "
            "multiples of 3, 'Buzz' for multiples of 5, and 'FizzBuzz' for "
            "multiples of both."
        ),
        "starter_code": (
            "n = int(input())\n"
            "# TODO: print the FizzBuzz sequence, one item per line\n"
        ),
        "test_cases": [
            {
                "input": "5\n",
                "expected_output": "1\n2\nFizz\n4\nBuzz",
                "is_hidden": False,
            },
            {
                "input": "15\n",
                "expected_output": "1\n2\nFizz\n4\nBuzz\nFizz\n7\n8\nFizz\nBuzz\n11\nFizz\n13\n14\nFizzBuzz",
                "is_hidden": True,
            },
        ],
    },
    {
        "slug": "is-prime",
        "title": "Prime Check",
        "concept": "loops",
        "difficulty": "medium",
        "description": (
            "Read an integer N (>= 2). Print 'YES' if it is prime, otherwise "
            "'NO'.\n\nExample: 7 -> YES, 9 -> NO."
        ),
        "starter_code": (
            "n = int(input())\n"
            "# TODO: print YES if n is prime, else NO\n"
        ),
        "test_cases": [
            {"input": "7\n", "expected_output": "YES", "is_hidden": False},
            {"input": "9\n", "expected_output": "NO", "is_hidden": False},
            {"input": "2\n", "expected_output": "YES", "is_hidden": True},
            {"input": "97\n", "expected_output": "YES", "is_hidden": True},
        ],
    },
    {
        "slug": "fibonacci",
        "title": "Nth Fibonacci",
        "concept": "recursion",
        "difficulty": "medium",
        "description": (
            "Read N (N >= 0). Print the Nth Fibonacci number, where "
            "fib(0) = 0, fib(1) = 1, fib(n) = fib(n-1) + fib(n-2)."
        ),
        "starter_code": (
            "def fib(n):\n"
            "    # TODO: implement (mind the two base cases)\n"
            "    pass\n\n"
            "n = int(input())\n"
            "print(fib(n))\n"
        ),
        "test_cases": [
            {"input": "0\n", "expected_output": "0", "is_hidden": False},
            {"input": "1\n", "expected_output": "1", "is_hidden": False},
            {"input": "10\n", "expected_output": "55", "is_hidden": True},
        ],
    },
]
