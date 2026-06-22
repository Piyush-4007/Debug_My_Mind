"""Phase 4 — Personalization.

Per-student concept mastery (Bayesian Knowledge Tracing), the misconception log,
and a next-problem recommender. The submit endpoint calls `record_attempt` after
grading; the `/api/profile/*` routes expose the resulting model to the student.
"""
from .tracing import record_attempt, BKT_PARAMS
from .routes import profile_bp

__all__ = ["record_attempt", "BKT_PARAMS", "profile_bp"]
