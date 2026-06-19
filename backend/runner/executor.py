"""Run student Python code against test cases and grade the output."""
from __future__ import annotations

import os
import platform
import subprocess
import sys
import tempfile
from dataclasses import dataclass

DEFAULT_TIMEOUT = 5  # seconds, per test case
MAX_OUTPUT_CHARS = 10_000  # truncate captured output / errors
MEMORY_LIMIT_BYTES = 256 * 1024 * 1024  # 256 MB (POSIX only)

IS_WINDOWS = platform.system() == "Windows"


@dataclass
class _Case:
    """Duck-typed view of a TestCase (ORM object or plain dict)."""

    input: str
    expected_output: str
    is_hidden: bool

    @classmethod
    def of(cls, tc) -> "_Case":
        if isinstance(tc, dict):
            return cls(tc.get("input", ""), tc.get("expected_output", ""),
                       bool(tc.get("is_hidden", False)))
        return cls(tc.input or "", tc.expected_output or "", bool(tc.is_hidden))


def _normalize(text: str) -> str:
    """Make output comparison forgiving of trailing whitespace / blank lines."""
    lines = [ln.rstrip() for ln in (text or "").replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def _apply_posix_limits():  # pragma: no cover - POSIX only, exercised on Render
    """Cap memory and CPU in the child process (called via preexec_fn)."""
    import resource

    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_LIMIT_BYTES, MEMORY_LIMIT_BYTES))
    cpu = DEFAULT_TIMEOUT + 1
    resource.setrlimit(resource.RLIMIT_CPU, (cpu, cpu))


def _run_python_once(code_path: str, stdin_text: str, timeout: int):
    """Run the Python file once. Returns (returncode, stdout, stderr, timed_out)."""
    kwargs = {}
    if not IS_WINDOWS:
        kwargs["preexec_fn"] = _apply_posix_limits

    try:
        # -I = isolated mode: ignore env vars, user site-packages, and PYTHON* vars.
        proc = subprocess.run(
            [sys.executable, "-I", code_path],
            input=stdin_text or "",
            capture_output=True,
            text=True,
            timeout=timeout,
            **kwargs,
        )
        return proc.returncode, proc.stdout, proc.stderr, False
    except subprocess.TimeoutExpired:
        return None, "", "", True


def _run_java_once(tmp: str, stdin_text: str, timeout: int):
    """Run the compiled Java `Main` once. (No rlimits — the JVM needs headroom.)"""
    try:
        proc = subprocess.run(
            # Explicit -cp so we don't depend on a global CLASSPATH including ".".
            ["java", "-Xmx256m", "-cp", tmp, "Main"],
            cwd=tmp,
            input=stdin_text or "",
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return proc.returncode, proc.stdout, proc.stderr, False
    except subprocess.TimeoutExpired:
        return None, "", "", True


def _clean_error(stderr: str, tmp: str) -> str:
    """Strip the temp path from tracebacks so students see relative names."""
    cleaned = (stderr or "").replace(tmp + os.sep, "").replace(tmp, "")
    return cleaned.strip()[:MAX_OUTPUT_CHARS]


def _summarize(results: list[dict]) -> dict:
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    if total and passed == total:
        status = "passed"
    elif passed == 0 and all(r["status"] in ("error", "timeout") for r in results):
        status = "error"
    else:
        status = "failed"
    return {"status": status, "passed_count": passed, "total_count": total, "results": results}


def _all_errored(cases: list[_Case], message: str) -> dict:
    """Every test fails with the same compile/syntax error."""
    results = [
        {"index": i, "is_hidden": c.is_hidden, "status": "error",
         "passed": False, "error": message,
         **({} if c.is_hidden else
            {"input": c.input, "expected_output": c.expected_output, "actual_output": ""})}
        for i, c in enumerate(cases)
    ]
    return _summarize(results)


def _grade(cases: list[_Case], run_one, tmp: str) -> dict:
    """Run each case through `run_one(stdin, timeout)` and grade the output."""
    results: list[dict] = []
    for i, c in enumerate(cases):
        rc, out, err, timed_out = run_one(c.input, DEFAULT_TIMEOUT)
        if timed_out:
            status, passed, error, actual = "timeout", False, (
                "Time limit exceeded — check for an infinite loop."), ""
        elif rc != 0:
            status, passed = "error", False
            error = _clean_error(err, tmp) or "Your program exited with an error."
            actual = out or ""
        else:
            actual = out or ""
            passed = _normalize(actual) == _normalize(c.expected_output)
            status = "passed" if passed else "failed"
            error = None

        result = {
            "index": i, "is_hidden": c.is_hidden, "status": status,
            "passed": passed, "error": error[:MAX_OUTPUT_CHARS] if error else None,
        }
        if not c.is_hidden:
            result["input"] = c.input
            result["expected_output"] = c.expected_output
            result["actual_output"] = actual[:MAX_OUTPUT_CHARS]
        results.append(result)
    return _summarize(results)


def run_submission(code: str, test_cases, language: str = "python",
                   timeout: int = DEFAULT_TIMEOUT) -> dict:
    """Grade `code` against `test_cases` in the given language ("python"|"java").

    Returns {status, passed_count, total_count, results[]} where each result is
    {index, is_hidden, status, passed, error, and (visible only) input/
    expected_output/actual_output}.
    """
    cases = [_Case.of(tc) for tc in test_cases]
    language = (language or "python").lower()

    if language == "java":
        return _run_java_submission(code, cases)
    return _run_python_submission(code, cases)


def _run_python_submission(code: str, cases: list[_Case]) -> dict:
    # Fast fail on syntax errors — no point running every test.
    try:
        compile(code, "submission.py", "exec")
    except SyntaxError as exc:
        return _all_errored(cases, f"SyntaxError: {exc.msg} (line {exc.lineno})")

    with tempfile.TemporaryDirectory() as tmp:
        code_path = os.path.join(tmp, "submission.py")
        with open(code_path, "w", encoding="utf-8") as fh:
            fh.write(code)
        return _grade(cases, lambda s, t: _run_python_once(code_path, s, t), tmp)


def _run_java_submission(code: str, cases: list[_Case]) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        with open(os.path.join(tmp, "Main.java"), "w", encoding="utf-8") as fh:
            fh.write(code)
        try:
            compiled = subprocess.run(
                ["javac", "Main.java"], cwd=tmp, capture_output=True,
                text=True, timeout=20,
            )
        except subprocess.TimeoutExpired:
            return _all_errored(cases, "Compilation timed out.")
        if compiled.returncode != 0:
            msg = _clean_error(compiled.stderr, tmp) or "Compilation failed."
            return _all_errored(cases, msg)
        return _grade(cases, lambda s, t: _run_java_once(tmp, s, t), tmp)
