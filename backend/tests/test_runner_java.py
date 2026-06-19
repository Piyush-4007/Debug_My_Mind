"""Java execution path of the runner.

Skipped automatically if a JDK (javac) isn't on PATH, so the suite still runs
on machines without Java.
"""
import shutil

import pytest

from runner import run_submission

pytestmark = pytest.mark.skipif(
    shutil.which("javac") is None, reason="JDK (javac) not installed"
)

TESTS = [
    {"input": "5\n", "expected_output": "15", "is_hidden": False},
    {"input": "100\n", "expected_output": "5050", "is_hidden": True},
]

GOOD = """import java.util.Scanner;
public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt(), total = 0;
        for (int i = 1; i <= n; i++) total += i;
        System.out.println(total);
    }
}"""


def test_java_correct_passes():
    out = run_submission(GOOD, TESTS, language="java")
    assert out["status"] == "passed"
    assert out["passed_count"] == 2


def test_java_wrong_fails():
    out = run_submission(GOOD.replace("i <= n", "i < n"), TESTS, language="java")
    assert out["status"] == "failed"
    assert out["passed_count"] == 0


def test_java_compile_error_reported():
    out = run_submission("public class Main { oops }", TESTS, language="java")
    assert out["status"] == "error"
    assert out["results"][0]["error"]  # a compiler message is surfaced
    # hidden test case must not leak its values
    hidden = [r for r in out["results"] if r["is_hidden"]][0]
    assert "expected_output" not in hidden
