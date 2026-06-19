"""Starter misconception catalog.

Each entry is a thinking error the diagnosis engine (Phase 3) will learn to
detect, paired with a focused micro-lesson. v1 target is ~30 entries; this is
the seed batch. `code` is the stable slug used by AST matchers / LLM prompts.
"""

MISCONCEPTIONS = [
    {
        "code": "off-by-one-range",
        "name": "Off-by-one with range() on an inclusive bound",
        "concept": "loops",
        "description": (
            "range(n) stops at n-1, so using range(n) when the problem includes n "
            "drops the final value. The fix is range(n + 1) (or range(1, n + 1))."
        ),
        "example_wrong_code": "total = 0\nfor i in range(n):      # misses n\n    total += i",
        "lesson": {
            "title": "range() is exclusive of its upper bound",
            "content": (
                "`range(n)` yields `0, 1, ..., n-1` — it never includes `n`. "
                "When a task says \"from 1 to n **inclusive**\", you need "
                "`range(1, n + 1)`. A quick check: `len(range(a, b)) == b - a`."
            ),
            "worked_example": (
                "# Sum 1..n inclusive\n"
                "total = 0\n"
                "for i in range(1, n + 1):   # includes n\n"
                "    total += i"
            ),
        },
    },
    {
        "code": "missing-base-case",
        "name": "Recursion without a (correct) base case",
        "concept": "recursion",
        "description": (
            "A recursive function that never hits a terminating condition recurses "
            "forever and raises RecursionError. Every recursion needs a base case "
            "reached before the recursive call."
        ),
        "example_wrong_code": (
            "def fact(n):\n    return n * fact(n - 1)   # never stops"
        ),
        "lesson": {
            "title": "Every recursion needs a base case",
            "content": (
                "Recursion works by reducing the problem toward a case you can "
                "answer directly. Without that base case the calls never stop and "
                "Python raises `RecursionError`. Ask: *what is the smallest input, "
                "and what do I return for it?*"
            ),
            "worked_example": (
                "def fact(n):\n"
                "    if n <= 1:        # base case\n"
                "        return 1\n"
                "    return n * fact(n - 1)"
            ),
        },
    },
    {
        "code": "mutable-default-arg",
        "name": "Mutable default argument",
        "concept": "functions",
        "description": (
            "Default argument values are evaluated once, at definition time. A "
            "default like []/{} is shared across all calls, so it accumulates state "
            "between calls unexpectedly."
        ),
        "example_wrong_code": (
            "def add(item, bucket=[]):   # shared across calls\n"
            "    bucket.append(item)\n"
            "    return bucket"
        ),
        "lesson": {
            "title": "Don't use mutable defaults",
            "content": (
                "`def f(x, acc=[])` creates **one** list reused by every call that "
                "omits `acc`. Use `None` as the sentinel and create a fresh object "
                "inside the function."
            ),
            "worked_example": (
                "def add(item, bucket=None):\n"
                "    if bucket is None:\n"
                "        bucket = []\n"
                "    bucket.append(item)\n"
                "    return bucket"
            ),
        },
    },
    {
        "code": "int-vs-float-division",
        "name": "Confusing / (float) with // (floor) division",
        "concept": "operators",
        "description": (
            "In Python 3, / always returns a float and // does floor division. "
            "Using / where an integer index/count is needed introduces a float; "
            "using // can silently drop the fractional part."
        ),
        "example_wrong_code": "mid = (lo + hi) / 2   # 2.5, not a valid index",
        "lesson": {
            "title": "/ gives a float, // floors to an int",
            "content": (
                "`7 / 2 == 3.5` (float) while `7 // 2 == 3` (int). For indices, "
                "midpoints, or counts you almost always want `//`. For exact ratios, "
                "use `/`. Mixing them up causes `TypeError: list indices must be "
                "integers` or off-by-fraction bugs."
            ),
            "worked_example": "mid = (lo + hi) // 2   # integer index",
        },
    },
    {
        "code": "string-immutability",
        "name": "Trying to mutate a string in place",
        "concept": "strings",
        "description": (
            "Strings are immutable; s[i] = 'x' raises TypeError. To 'change' a "
            "string, build a new one (slicing, join, or a list of chars)."
        ),
        "example_wrong_code": "s[0] = 'H'   # TypeError: 'str' object does not support item assignment",
        "lesson": {
            "title": "Strings can't be edited in place",
            "content": (
                "Unlike lists, strings are immutable — every 'edit' creates a new "
                "string. Convert to a list of characters and `''.join(...)`, or use "
                "slicing/concatenation to assemble the new value."
            ),
            "worked_example": (
                "chars = list(s)\n"
                "chars[0] = 'H'\n"
                "s = ''.join(chars)"
            ),
        },
    },
    {
        "code": "index-out-of-range",
        "name": "Indexing past the end of a list",
        "concept": "lists",
        "description": (
            "Valid indices are 0..len(lst)-1. Looping while i <= len(lst) or "
            "accessing lst[len(lst)] raises IndexError."
        ),
        "example_wrong_code": (
            "for i in range(len(lst) + 1):   # last i is out of range\n"
            "    print(lst[i])"
        ),
        "lesson": {
            "title": "The last valid index is len(lst) - 1",
            "content": (
                "A list of length `n` has indices `0` to `n-1`. `lst[n]` is always "
                "out of range. To visit every element, use `range(len(lst))` or, "
                "better, iterate directly: `for x in lst:`."
            ),
            "worked_example": (
                "for x in lst:        # no index arithmetic needed\n"
                "    print(x)"
            ),
        },
    },
]
