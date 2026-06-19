from runner import run_submission

CASES = [
    {"input": "5\n", "expected_output": "15", "is_hidden": False},
    {"input": "1\n", "expected_output": "1", "is_hidden": False},
    {"input": "100\n", "expected_output": "5050", "is_hidden": True},
]

CORRECT = "n = int(input())\nprint(sum(range(1, n + 1)))\n"
WRONG = "n = int(input())\nprint(sum(range(1, n)))\n"  # off-by-one, drops n


def test_correct_solution_passes_all():
    out = run_submission(CORRECT, CASES)
    assert out["status"] == "passed"
    assert out["passed_count"] == 3
    assert out["total_count"] == 3


def test_wrong_solution_fails():
    out = run_submission(WRONG, CASES)
    assert out["status"] == "failed"
    assert out["passed_count"] == 0


def test_hidden_test_values_not_leaked():
    out = run_submission(CORRECT, CASES)
    hidden = [r for r in out["results"] if r["is_hidden"]]
    assert hidden and all("expected_output" not in r for r in hidden)
    visible = [r for r in out["results"] if not r["is_hidden"]]
    assert all("expected_output" in r for r in visible)


def test_syntax_error_reported():
    out = run_submission("n = int(input()\nprint(n)", CASES)  # missing paren
    assert out["status"] == "error"
    assert "SyntaxError" in out["results"][0]["error"]


def test_runtime_error_reported():
    out = run_submission("raise ValueError('boom')", CASES)
    assert out["status"] == "error"
    assert "ValueError" in out["results"][0]["error"]


def test_infinite_loop_times_out():
    out = run_submission("while True:\n    pass", CASES, timeout=2)
    assert out["results"][0]["status"] == "timeout"
    assert out["passed_count"] == 0


def test_trailing_whitespace_is_forgiven():
    # Extra trailing newline should still count as correct.
    code = "n = int(input())\nprint(sum(range(1, n + 1)))\nprint()\n"
    out = run_submission(code, [{"input": "5\n", "expected_output": "15", "is_hidden": False}])
    assert out["passed_count"] == 1
