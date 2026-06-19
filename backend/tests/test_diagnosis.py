"""Tests for the rule-based half of the diagnosis pipeline (no network)."""
from diagnosis import ast_analyzer
from diagnosis.verifier import reconcile


def codes(candidates):
    return [c["code"] for c in candidates]


def test_mutable_default_arg_detected():
    code = "def add(x, bucket=[]):\n    bucket.append(x)\n    return bucket\n"
    assert "mutable-default-arg" in codes(ast_analyzer.analyze(code))


def test_missing_base_case_detected():
    code = "def fact(n):\n    return n * fact(n - 1)\n"
    out = ast_analyzer.analyze(code)
    assert out and out[0]["code"] == "missing-base-case"


def test_correct_recursion_not_flagged_as_missing_base_case():
    code = "def fact(n):\n    if n <= 1:\n        return 1\n    return n * fact(n - 1)\n"
    assert "missing-base-case" not in codes(ast_analyzer.analyze(code))


def test_range_len_plus_one_is_index_out_of_range():
    code = "for i in range(len(lst) + 1):\n    print(lst[i])\n"
    assert "index-out-of-range" in codes(ast_analyzer.analyze(code))


def test_float_division_index():
    code = "mid = lst[(lo + hi) / 2]\n"
    assert "int-vs-float-division" in codes(ast_analyzer.analyze(code))


def test_runtime_error_signature_recursionerror():
    out = ast_analyzer.analyze("def f(n):\n    return f(n)\n",
                               error_text="RecursionError: maximum recursion depth exceeded")
    assert out[0]["code"] == "missing-base-case"
    assert out[0]["confidence"] >= 0.9


def test_string_immutability_from_error_signal():
    out = ast_analyzer.analyze(
        "s[0] = 'H'\n",
        error_text="TypeError: 'str' object does not support item assignment",
    )
    assert out[0]["code"] == "string-immutability"


def test_syntax_error_still_returns_error_signals_gracefully():
    # Unparseable code shouldn't raise; error signals still apply.
    out = ast_analyzer.analyze("def (:", error_text="IndexError: list index out of range")
    assert "index-out-of-range" in codes(out)


# --- verifier ---

def test_verifier_agreement_is_high_confidence():
    ast_c = [{"code": "missing-base-case", "confidence": 0.85, "evidence": "x"}]
    llm = {"misconception_code": "missing-base-case", "confidence": 0.9,
           "explanation": "no base case", "fix_hint": "add one"}
    v = reconcile(ast_c, llm)
    assert v["code"] == "missing-base-case"
    assert v["confidence_band"] == "high"
    assert v["agreement"] is True


def test_verifier_disagreement_flags_low_or_medium():
    ast_c = [{"code": "off-by-one-range", "confidence": 0.4, "evidence": "x"}]
    llm = {"misconception_code": "index-out-of-range", "confidence": 0.7,
           "explanation": "e", "fix_hint": "f"}
    v = reconcile(ast_c, llm)
    assert v["agreement"] is False
    assert v["confidence_band"] in ("low", "medium")


def test_verifier_none_when_no_signal():
    assert reconcile([], None) is None
