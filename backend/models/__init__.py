"""SQLAlchemy models for DebugMyMind (Phase 1 schema).

Importing this package registers every model on the shared `db` metadata so
`db.create_all()` sees them.
"""
from .user import User
from .problem import Problem, TestCase
from .submission import Submission
from .misconception import Misconception
from .lesson import Lesson
from .profile import StudentProfile

__all__ = [
    "User",
    "Problem",
    "TestCase",
    "Submission",
    "Misconception",
    "Lesson",
    "StudentProfile",
]
