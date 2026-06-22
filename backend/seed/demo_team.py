"""Seed three named demo students (the project team) with *genuine* activity.

Unlike `cohort.py` (which fabricates rows for bulk), this runs real code through
the actual pipeline — runner → diagnosis → BKT — exactly like the submit
endpoint. So every diagnosed misconception and mastery score you see in the demo
was really produced by the system. Use this to drive a live walkthrough.

Each student has a personality:
  • Piyush — strong; mostly correct, one slip he then fixes.
  • Vinit  — improving; a couple of classic bugs, then corrects them.
  • Ketan  — struggling with recursion & strings; several real misconceptions.

Run with:  flask --app app seed-demo   (run `seed` first for the problem bank)
Idempotent: skips students that already exist.
"""
from __future__ import annotations

import click

from diagnosis import diagnose_submission
from extensions import db
from models import Problem, Submission, User
from profile import record_attempt
from runner import run_submission

# --- Correct, fully-passing solutions ------------------------------------
CORRECT = {
    "sum-to-n": "n = int(input())\nprint(sum(range(1, n + 1)))\n",
    "factorial": "def fact(n):\n    return 1 if n == 0 else n * fact(n - 1)\n\nn = int(input())\nprint(fact(n))\n",
    "fibonacci": "def fib(n):\n    return n if n < 2 else fib(n - 1) + fib(n - 2)\n\nn = int(input())\nprint(fib(n))\n",
    "is-prime": (
        "n = int(input())\n"
        "if n < 2:\n    print('NO')\n"
        "else:\n"
        "    p = True\n"
        "    for i in range(2, int(n ** 0.5) + 1):\n"
        "        if n % i == 0:\n            p = False\n            break\n"
        "    print('YES' if p else 'NO')\n"
    ),
    "sum-of-digits": "n = input().strip()\nprint(sum(int(c) for c in n))\n",
    "count-vowels": "s = input()\nprint(sum(1 for c in s.lower() if c in 'aeiou'))\n",
    "reverse-string": "print(input()[::-1])\n",
    "even-or-odd": "n = int(input())\nprint('Even' if n % 2 == 0 else 'Odd')\n",
    "leap-year": "y = int(input())\nprint('YES' if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 'NO')\n",
    "max-in-list": (
        "n = int(input())\nnums = list(map(int, input().split()))\n"
        "m = nums[0]\nfor x in nums:\n    if x > m:\n        m = x\nprint(m)\n"
    ),
    "count-evens": (
        "n = int(input())\nnums = list(map(int, input().split()))\n"
        "print(sum(1 for x in nums if x % 2 == 0))\n"
    ),
    "fizzbuzz": (
        "n = int(input())\n"
        "for i in range(1, n + 1):\n"
        "    if i % 15 == 0:\n        print('FizzBuzz')\n"
        "    elif i % 3 == 0:\n        print('Fizz')\n"
        "    elif i % 5 == 0:\n        print('Buzz')\n"
        "    else:\n        print(i)\n"
    ),
}

# --- Wrong solutions, each crafted to trigger a real misconception --------
WRONG = {
    # off-by-one-range: range stops one short of the inclusive bound.
    "sum-to-n-offbyone": "n = int(input())\nprint(sum(range(1, n)))\n",
    # missing-base-case: recursion with no terminating return -> RecursionError.
    "factorial-nobase": "def fact(n):\n    return n * fact(n - 1)\n\nn = int(input())\nprint(fact(n))\n",
    "fibonacci-nobase": "def fib(n):\n    return fib(n - 1) + fib(n - 2)\n\nn = int(input())\nprint(fib(n))\n",
    # string-immutability: assigning to a string index -> TypeError.
    "reverse-immutable": (
        "s = input()\nr = s\n"
        "for i in range(len(s)):\n    r[i] = s[len(s) - 1 - i]\nprint(r)\n"
    ),
    # index-out-of-range: range(len(nums)+1) walks one past the end -> IndexError.
    "max-indexerror": (
        "n = int(input())\nnums = list(map(int, input().split()))\n"
        "m = nums[0]\nfor i in range(len(nums) + 1):\n"
        "    if nums[i] > m:\n        m = nums[i]\nprint(m)\n"
    ),
    # leap-year: forgets the century rule (fails 1900). No catalogued AST match;
    # still recorded as a failed conditionals attempt.
    "leap-naive": "y = int(input())\nprint('YES' if y % 4 == 0 else 'NO')\n",
}

# Per-student scripts: ordered (problem_slug, code_key). "Wrong then correct"
# pairs demonstrate the misconception diagnosis *and* recovery in the mastery curve.
TEAM = {
    ("Piyush Singh", "piyush@team.dev"): [
        ("sum-to-n", "sum-to-n"),
        ("factorial", "factorial"),
        ("is-prime", "is-prime"),
        ("fibonacci", "fibonacci"),
        ("sum-of-digits", "sum-of-digits"),
        ("count-vowels", "count-vowels"),
        ("max-in-list", "max-in-list"),
        ("leap-year", "leap-naive"),     # one slip…
        ("leap-year", "leap-year"),       # …then fixes it
        ("even-or-odd", "even-or-odd"),
    ],
    ("Vinit Pal", "vinit@team.dev"): [
        ("sum-to-n", "sum-to-n-offbyone"),  # off-by-one
        ("sum-to-n", "sum-to-n"),            # corrected
        ("reverse-string", "reverse-string"),
        ("count-vowels", "count-vowels"),
        ("fizzbuzz", "fizzbuzz"),
        ("max-in-list", "max-indexerror"),   # index error
        ("max-in-list", "max-in-list"),       # corrected
        ("even-or-odd", "even-or-odd"),
        ("factorial", "factorial"),
    ],
    ("Ketan Bhendarkar", "ketan@team.dev"): [
        ("factorial", "factorial-nobase"),   # missing base case
        ("fibonacci", "fibonacci-nobase"),    # missing base case
        ("reverse-string", "reverse-immutable"),  # string immutability
        ("sum-to-n", "sum-to-n-offbyone"),    # off-by-one
        ("sum-to-n", "sum-to-n"),              # corrected
        ("leap-year", "leap-naive"),
        ("count-vowels", "count-vowels"),
        ("even-or-odd", "even-or-odd"),
    ],
}

_CODES = {**CORRECT, **WRONG}


def _grade_and_record(student: User, problem: Problem, code: str) -> str:
    """Mirror the submit endpoint: grade, diagnose, persist, update mastery."""
    outcome = run_submission(code, problem.test_cases, language="python")
    submission = Submission(
        user_id=student.id,
        problem_id=problem.id,
        code=code,
        language="python",
        status=outcome["status"],
        passed_count=outcome["passed_count"],
        total_count=outcome["total_count"],
    )
    if outcome["status"] != "passed":
        diagnosis = diagnose_submission(
            code,
            {"title": problem.title, "description": problem.description},
            outcome["results"],
            language="python",
        )
        if diagnosis and diagnosis.get("misconception"):
            submission.misconception_id = diagnosis["misconception"]["id"]
    db.session.add(submission)
    db.session.commit()
    record_attempt(student.id, problem.concept, correct=outcome["status"] == "passed")
    return outcome["status"]


def run_demo_seed() -> None:
    problems = {p.slug: p for p in Problem.query.all()}
    if not problems:
        click.echo("Run `seed` first — no problem bank to submit against.")
        return

    created = 0
    for (name, email), script in TEAM.items():
        if User.query.filter_by(email=email).first():
            click.echo(f"  {name} already exists — skipping.")
            continue

        student = User(name=name, email=email, role="student")
        student.set_password("password")
        db.session.add(student)
        db.session.commit()

        passed = failed = 0
        for slug, code_key in script:
            problem = problems.get(slug)
            if problem is None:
                continue
            status = _grade_and_record(student, problem, _CODES[code_key])
            if status == "passed":
                passed += 1
            else:
                failed += 1
        created += 1
        click.echo(f"  {name}: {passed} passed, {failed} failed across {len(script)} submissions.")

    db.session.commit()
    if created:
        click.echo(
            f"Seeded {created} demo team student(s) "
            f"(piyush@team.dev / vinit@team.dev / ketan@team.dev, password 'password')."
        )
    else:
        click.echo("Demo team already present — nothing to add.")
