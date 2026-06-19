from __future__ import annotations

from extensions import db
from .base import TimestampMixin


class Misconception(TimestampMixin, db.Model):
    """A catalogued thinking error behind a class of wrong answers.

    The diagnosis engine (Phase 3) maps a failed submission to one of these.
    Each has an associated micro-lesson (one-to-one with Lesson).
    """

    __tablename__ = "misconceptions"

    id = db.Column(db.Integer, primary_key=True)
    # stable slug used by AST matchers / LLM prompts, e.g. "off-by-one-range"
    code = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    concept = db.Column(db.String(60), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False, default="")
    example_wrong_code = db.Column(db.Text, nullable=False, default="")

    lesson = db.relationship(
        "Lesson",
        back_populates="misconception",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def to_dict(self, include_lesson: bool = False) -> dict:
        data = {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "concept": self.concept,
            "description": self.description,
            "example_wrong_code": self.example_wrong_code,
        }
        if include_lesson and self.lesson is not None:
            data["lesson"] = self.lesson.to_dict()
        return data
