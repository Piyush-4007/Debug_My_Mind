"""Reconcile AST and LLM diagnoses into a single verdict with a confidence band.

This cross-checking step is the project's research contribution: agreement
between an independent rule-based signal and the LLM yields high confidence;
disagreement is surfaced rather than hidden.
"""
from __future__ import annotations

STRONG = 0.85  # AST confidence at/above which we trust structure/error signatures


def reconcile(ast_candidates: list[dict], llm: dict | None) -> dict | None:
    """Combine signals. Returns a verdict dict or None if nothing was found.

    Verdict: {code, confidence_band, agreement, explanation, fix_hint, sources}
    where confidence_band is "high" | "medium" | "low".
    """
    ast_top = ast_candidates[0] if ast_candidates else None
    llm_code = None
    if llm and llm.get("misconception_code"):
        llm_code = llm["misconception_code"]

    sources = {"ast": ast_candidates[:3], "llm": llm}

    def verdict(code, band, agreement):
        explanation = (llm or {}).get("explanation", "") if llm else ""
        fix_hint = (llm or {}).get("fix_hint", "") if llm else ""
        return {
            "code": code,
            "confidence_band": band,
            "agreement": agreement,
            "explanation": explanation,
            "fix_hint": fix_hint,
            "sources": sources,
        }

    # 1. Both agree → high confidence.
    if ast_top and llm_code and ast_top["code"] == llm_code:
        return verdict(ast_top["code"], "high", True)

    # 2. Strong AST signal (e.g. RecursionError, mutable default) → trust it.
    if ast_top and ast_top["confidence"] >= STRONG:
        return verdict(ast_top["code"], "high" if not llm_code else "medium", False)

    # 3. LLM has an opinion, AST weak/absent → medium, flagged as unverified.
    if llm_code:
        return verdict(llm_code, "medium" if not ast_top else "low", False)

    # 4. Only a weak AST hint.
    if ast_top:
        return verdict(ast_top["code"], "low", False)

    return None
