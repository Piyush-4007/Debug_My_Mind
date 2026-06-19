"""Sandboxed code execution for student submissions (Phase 2).

Strategy (decided for the pilot): run each submission in a fresh Python
subprocess with a hard wall-clock timeout. On POSIX (Render/Linux prod) we also
apply address-space and CPU rlimits; on Windows dev the timeout is the guard.

This is sufficient isolation for a trusted classroom pilot. Stronger isolation
(Docker-per-run) can replace `executor` later without touching callers.
"""
from .executor import run_submission

__all__ = ["run_submission"]
