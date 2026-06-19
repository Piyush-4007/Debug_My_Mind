from __future__ import annotations

from extensions import db
from .base import TimestampMixin


class Problem(TimestampMixin, db.Model):
    __tablename__ = "problems"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    # e.g. "loops", "recursion", "lists", "functions", "strings", "conditionals"
    concept = db.Column(db.String(60), nullable=False, index=True)
    # "easy" | "medium" | "hard"
    difficulty = db.Column(db.String(20), nullable=False, default="easy")
    # signature/stub shown in the editor (Phase 2 uses this in Monaco)
    starter_code = db.Column(db.Text, nullable=False, default="")

    test_cases = db.relationship(
        "TestCase",
        back_populates="problem",
        cascade="all, delete-orphan",
        order_by="TestCase.ordering",
    )
    submissions = db.relationship(
        "Submission", back_populates="problem", cascade="all, delete-orphan"
    )

    def to_dict(self, include_hidden_tests: bool = False) -> dict:
        visible = [
            tc.to_dict()
            for tc in self.test_cases
            if include_hidden_tests or not tc.is_hidden
        ]
        return {
            "id": self.id,
            "slug": self.slug,
            "title": self.title,
            "description": self.description,
            "concept": self.concept,
            "difficulty": self.difficulty,
            "starter_code": self.starter_code,
            "test_cases": visible,
            "test_case_count": len(self.test_cases),
        }


class TestCase(db.Model):
    __tablename__ = "test_cases"

    id = db.Column(db.Integer, primary_key=True)
    problem_id = db.Column(
        db.Integer, db.ForeignKey("problems.id", ondelete="CASCADE"), nullable=False
    )
    # stdin fed to the program (Phase 2 runner)
    input = db.Column(db.Text, nullable=False, default="")
    expected_output = db.Column(db.Text, nullable=False, default="")
    # hidden tests are graded but not shown to the student
    is_hidden = db.Column(db.Boolean, nullable=False, default=False)
    ordering = db.Column(db.Integer, nullable=False, default=0)

    problem = db.relationship("Problem", back_populates="test_cases")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "input": self.input,
            "expected_output": self.expected_output,
            "is_hidden": self.is_hidden,
            "ordering": self.ordering,
        }
