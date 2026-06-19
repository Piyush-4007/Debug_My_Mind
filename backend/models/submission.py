from __future__ import annotations

from extensions import db
from .base import TimestampMixin


class Submission(TimestampMixin, db.Model):
    """A student's code attempt on a problem.

    Phase 1 stores the record; Phase 2 fills in test results; Phase 3 attaches
    a diagnosed misconception.
    """

    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    problem_id = db.Column(
        db.Integer, db.ForeignKey("problems.id", ondelete="CASCADE"), nullable=False
    )
    code = db.Column(db.Text, nullable=False)
    # "pending" | "passed" | "failed" | "error"
    status = db.Column(db.String(20), nullable=False, default="pending")
    passed_count = db.Column(db.Integer, nullable=False, default=0)
    total_count = db.Column(db.Integer, nullable=False, default=0)

    # Phase 3: which misconception we diagnosed (nullable until then).
    misconception_id = db.Column(
        db.Integer, db.ForeignKey("misconceptions.id", ondelete="SET NULL"), nullable=True
    )

    user = db.relationship("User", back_populates="submissions")
    problem = db.relationship("Problem", back_populates="submissions")
    misconception = db.relationship("Misconception")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "problem_id": self.problem_id,
            "code": self.code,
            "status": self.status,
            "passed_count": self.passed_count,
            "total_count": self.total_count,
            "misconception_id": self.misconception_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
