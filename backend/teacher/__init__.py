"""Phase 5 — Teacher Dashboard.

Class-level aggregation over the per-student model built in Phase 4: cohort
concept mastery, the most common misconceptions across the class, a student
roster, and a per-student drilldown. All routes are teacher-only.
"""
from .routes import teacher_bp

__all__ = ["teacher_bp"]
