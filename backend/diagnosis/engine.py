"""Diagnosis orchestrator: AST + LLM + verifier → a misconception + micro-lesson.

Entry point `diagnose_submission(...)` is called from the submit endpoint when a
submission fails. It is defensive: any internal failure returns None so grading
still succeeds without a diagnosis.
"""
from __future__ import annotations

import logging

from models import Misconception
from . import ast_analyzer, llm_client, verifier

log = logging.getLogger(__name__)


def _collect_failure(results: list[dict]) -> tuple[str, str]:
    """Build (error_text, failure_summary) from graded results.

    error_text feeds the AST error-signature matcher; failure_summary is the
    human-readable context handed to the LLM. Only visible-test values are used.
    """
    errors, summary = [], []
    for r in results:
        if r.get("passed"):
            continue
        if r.get("error"):
            errors.append(r["error"])
        if not r.get("is_hidden"):
            summary.append(
                f"input={r.get('input', '')!r} expected={r.get('expected_output', '')!r} "
                f"got={r.get('actual_output', '')!r}"
                + (f" error={r['error']}" if r.get("error") else "")
            )
    return "\n".join(errors), "\n".join(summary[:5])


def _catalog() -> list[dict]:
    return [
        {"code": m.code, "name": m.name, "concept": m.concept}
        for m in Misconception.query.all()
    ]


def diagnose_submission(code: str, problem: dict, results: list[dict],
                        language: str = "python") -> dict | None:
    """Return a diagnosis dict (with misconception + lesson) or None."""
    try:
        error_text, failure_summary = _collect_failure(results)

        # The AST matchers are Python-specific; skip them for other languages
        # (Java leans on the LLM + runtime-error reasoning instead).
        ast_candidates = (
            ast_analyzer.analyze(code, error_text) if language == "python" else []
        )

        catalog = _catalog()
        llm = llm_client.llm_diagnose(code, problem, failure_summary, catalog, language)

        verdict = verifier.reconcile(ast_candidates, llm)
        misconception = (
            Misconception.query.filter_by(code=verdict["code"]).first()
            if verdict
            else None
        )

        # Full diagnosis: a catalogued misconception (with its micro-lesson).
        if misconception is not None:
            return {
                "misconception": misconception.to_dict(include_lesson=True),
                "confidence": verdict["confidence_band"],
                "agreement": verdict["agreement"],
                "explanation": verdict["explanation"] or misconception.description,
                "fix_hint": verdict["fix_hint"],
                "sources": verdict["sources"],
            }

        # Fallback: no catalogued misconception matched, but the LLM can still
        # explain what went wrong (e.g. NameError, forgot to read input). Show
        # general feedback without a lesson rather than nothing.
        if llm and llm.get("explanation"):
            return {
                "misconception": None,
                "confidence": "info",
                "agreement": False,
                "explanation": llm["explanation"],
                "fix_hint": llm.get("fix_hint", ""),
                "sources": {"ast": ast_candidates[:3], "llm": llm},
            }

        if verdict:
            log.info("Verdict code %r not in catalog and no LLM text.", verdict["code"])
        return None
    except Exception as exc:  # never let diagnosis break grading
        log.warning("diagnose_submission failed: %s", exc)
        return None
