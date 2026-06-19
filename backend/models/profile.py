from __future__ import annotations

from extensions import db
from .base import TimestampMixin


class StudentProfile(TimestampMixin, db.Model):
    """Per-student, per-concept mastery row.

    Phase 1 defines the shape; Phase 4 (knowledge tracing) populates and updates
    `mastery_score` as students submit.
    """

    __tablename__ = "student_profiles"
    __table_args__ = (
        db.UniqueConstraint("user_id", "concept", name="uq_student_concept"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    concept = db.Column(db.String(60), nullable=False, index=True)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    correct = db.Column(db.Integer, nullable=False, default=0)
    # 0.0–1.0 mastery estimate (Bayesian KT in Phase 4)
    mastery_score = db.Column(db.Float, nullable=False, default=0.0)

    user = db.relationship("User", back_populates="profiles")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "concept": self.concept,
            "attempts": self.attempts,
            "correct": self.correct,
            "mastery_score": self.mastery_score,
        }
