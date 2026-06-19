"""Rule-based misconception detection via Python AST + runtime-error signals.

This is the reliable, free, deterministic half of the hybrid pipeline. It emits
*candidate* misconceptions (by catalog `code`) with a confidence in [0, 1] and a
short human-readable evidence string. The verifier later reconciles these with
the LLM's opinion.

Confidence guide:
  >= 0.85  strong (runtime error signature or unambiguous structure)
  ~ 0.7    good structural signal
  <= 0.5   weak hint; needs LLM corroboration
"""
from __future__ import annotations

import ast

# Substrings in a runtime traceback that strongly imply a misconception.
ERROR_SIGNALS = [
    ("does not support item assignment", "string-immutability", 0.95),
    ("maximum recursion depth", "missing-base-case", 0.95),
    ("RecursionError", "missing-base-case", 0.95),
    ("list indices must be integers", "int-vs-float-division", 0.85),
    ("string index out of range", "index-out-of-range", 0.9),
    ("list index out of range", "index-out-of-range", 0.9),
    ("IndexError", "index-out-of-range", 0.8),
]


def _is_name(node, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name


def _contains_len(node) -> bool:
    return any(
        isinstance(c, ast.Call) and _is_name(c.func, "len") for c in ast.walk(node)
    )


def _is_recursive(func: ast.FunctionDef) -> bool:
    return any(
        isinstance(n, ast.Call) and _is_name(n.func, func.name)
        for n in ast.walk(func)
    )


def _has_base_case(func: ast.FunctionDef) -> bool:
    """True if some return path does not recurse (i.e. a real base case exists)."""
    for ret in (n for n in ast.walk(func) if isinstance(n, ast.Return)):
        recurses = ret.value is not None and any(
            isinstance(c, ast.Call) and _is_name(c.func, func.name)
            for c in ast.walk(ret)
        )
        if not recurses:
            return True
    return False


def analyze(code: str, error_text: str = "") -> list[dict]:
    """Return candidate misconceptions sorted by confidence (highest first)."""
    candidates: dict[str, tuple[float, str]] = {}

    def add(mc_code: str, confidence: float, evidence: str) -> None:
        if mc_code not in candidates or confidence > candidates[mc_code][0]:
            candidates[mc_code] = (confidence, evidence)

    # 1. Runtime-error signatures (most reliable).
    haystack = (error_text or "").lower()
    for needle, mc_code, conf in ERROR_SIGNALS:
        if needle.lower() in haystack:
            add(mc_code, conf, f'Runtime error mentioned “{needle}”.')

    # 2. Structural patterns.
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return _sorted(candidates)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Mutable default argument.
            for default in node.args.defaults + [d for d in node.args.kw_defaults if d]:
                if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                    add(
                        "mutable-default-arg",
                        0.9,
                        f'Function “{node.name}” uses a mutable default argument.',
                    )
            # Recursion without a base case.
            if _is_recursive(node) and not _has_base_case(node):
                add(
                    "missing-base-case",
                    0.85,
                    f'Recursive function “{node.name}” has no non-recursive return.',
                )

        # Assigning to an indexed element (invalid for strings).
        if isinstance(node, ast.Assign):
            if any(isinstance(t, ast.Subscript) for t in node.targets):
                add(
                    "string-immutability",
                    0.5,
                    "Assigns to an indexed element — fails if the target is a string.",
                )

        # range(...) shapes.
        if isinstance(node, ast.Call) and _is_name(node.func, "range") and len(node.args) == 1:
            arg = node.args[0]
            if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add) and _contains_len(arg):
                add(
                    "index-out-of-range",
                    0.7,
                    "Loops over range(len(...) + 1), indexing one past the end.",
                )
            elif isinstance(arg, ast.Name):
                add(
                    "off-by-one-range",
                    0.4,
                    f"Loop uses range({arg.id}); range stops one short of an inclusive bound.",
                )

        # Float division used as an index.
        if isinstance(node, ast.Subscript):
            idx = node.slice
            if isinstance(idx, ast.BinOp) and isinstance(idx.op, ast.Div):
                add(
                    "int-vs-float-division",
                    0.7,
                    "Uses / (float division) to compute an index; needs // .",
                )

    return _sorted(candidates)


def _sorted(candidates: dict[str, tuple[float, str]]) -> list[dict]:
    out = [
        {"code": code, "confidence": round(conf, 2), "evidence": ev}
        for code, (conf, ev) in candidates.items()
    ]
    out.sort(key=lambda c: c["confidence"], reverse=True)
    return out
