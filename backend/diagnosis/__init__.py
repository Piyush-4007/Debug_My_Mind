"""Hybrid misconception-diagnosis engine (Phase 3).

AST static analysis + LLM reasoning + a verifier that cross-checks them.
"""
from .engine import diagnose_submission

__all__ = ["diagnose_submission"]
