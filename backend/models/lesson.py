from __future__ import annotations

from extensions import db
from .base import TimestampMixin


class Lesson(TimestampMixin, db.Model):
    """A short, focused micro-lesson tied to one misconception."""

    __tablename__ = "lessons"

    id = db.Column(db.Integer, primary_key=True)
    misconception_id = db.Column(
        db.Integer,
        db.ForeignKey("misconceptions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    title = db.Column(db.String(200), nullable=False)
    # Markdown body of the explanation.
    content = db.Column(db.Text, nullable=False)
    # A corrected / worked example the student can compare against.
    worked_example = db.Column(db.Text, nullable=False, default="")

    misconception = db.relationship("Misconception", back_populates="lesson")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "misconception_id": self.misconception_id,
            "title": self.title,
            "content": self.content,
            "worked_example": self.worked_example,
        }
