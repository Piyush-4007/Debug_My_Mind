"""Next-problem recommender.

Strategy: target the student's *weakest* concepts (lowest BKT mastery), and
within a concept prefer problems they haven't solved yet, ordered by difficulty
so practice ramps gently. Concepts the student has never touched are treated as
weak (prior mastery) so the recommender also encourages breadth.
"""
from __future__ import annotations

from models import Problem, Submission, StudentProfile
from .tracing import BKT_PARAMS, MASTERY_THRESHOLD

_DIFFICULTY_ORDER = {"easy": 0, "medium": 1, "hard": 2}


def recommend(user_id: int, limit: int = 6) -> list[dict]:
    """Return up to `limit` recommended problems for a student, weakest-first."""
    # Mastery per concept (default to the BKT prior for untouched concepts).
    mastery = {
        p.concept: p.mastery_score
        for p in StudentProfile.query.filter_by(user_id=user_id).all()
    }

    # Slugs the student has already solved — don't recommend solved work.
    solved = {
        s.problem_id
        for s in Submission.query.filter_by(user_id=user_id, status="passed").all()
    }

    candidates = []
    for prob in Problem.query.all():
        if prob.id in solved:
            continue
        score = mastery.get(prob.concept, BKT_PARAMS["p_init"])
        candidates.append((score, _DIFFICULTY_ORDER.get(prob.difficulty, 1), prob))

    # Weakest concept first; gentler difficulty first within a concept.
    candidates.sort(key=lambda c: (c[0], c[1], c[2].id))

    out = []
    for mastery_score, _, prob in candidates[:limit]:
        out.append(
            {
                "slug": prob.slug,
                "title": prob.title,
                "concept": prob.concept,
                "difficulty": prob.difficulty,
                "languages": prob.languages or ["python"],
                "concept_mastery": round(mastery_score, 4),
                "reason": _reason(prob.concept, mastery_score),
            }
        )
    return out


def _reason(concept: str, mastery: float) -> str:
    if mastery < 0.3:
        return f"Build core confidence in {concept}"
    if mastery < MASTERY_THRESHOLD:
        return f"Strengthen your {concept} skills"
    return f"Keep {concept} sharp"
