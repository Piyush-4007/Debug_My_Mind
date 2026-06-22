"""Student personalization API: mastery overview, misconception log, recommendations."""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.orm import joinedload

from models import Misconception, Problem, StudentProfile, Submission
from .recommender import recommend
from .tracing import MASTERY_THRESHOLD

profile_bp = Blueprint("profile", __name__, url_prefix="/api/profile")


@profile_bp.get("")
@jwt_required()
def overview():
    """Mastery per concept + headline stats for the current student."""
    user_id = int(get_jwt_identity())

    profiles = (
        StudentProfile.query.filter_by(user_id=user_id)
        .order_by(StudentProfile.mastery_score.asc())
        .all()
    )
    concepts = [
        {
            "concept": p.concept,
            "attempts": p.attempts,
            "correct": p.correct,
            "mastery_score": p.mastery_score,
            "mastered": p.mastery_score >= MASTERY_THRESHOLD,
        }
        for p in profiles
    ]

    total_attempts = sum(p.attempts for p in profiles)
    total_correct = sum(p.correct for p in profiles)
    mastered = sum(1 for p in profiles if p.mastery_score >= MASTERY_THRESHOLD)
    # Weakest concepts the student has actually practised.
    weak_spots = [c["concept"] for c in concepts if not c["mastered"]][:3]

    return jsonify(
        concepts=concepts,
        stats={
            "concepts_tracked": len(concepts),
            "concepts_mastered": mastered,
            "total_attempts": total_attempts,
            "total_correct": total_correct,
            "accuracy": round(total_correct / total_attempts, 3) if total_attempts else 0.0,
        },
        weak_spots=weak_spots,
        mastery_threshold=MASTERY_THRESHOLD,
    )


@profile_bp.get("/misconceptions")
@jwt_required()
def misconception_log():
    """The student's diagnosed misconceptions, most frequent first."""
    user_id = int(get_jwt_identity())

    subs = (
        Submission.query.filter(
            Submission.user_id == user_id,
            Submission.misconception_id.isnot(None),
        )
        .options(joinedload(Submission.misconception))
        .order_by(Submission.created_at.desc())
        .all()
    )

    # Aggregate by misconception, keeping the most recent occurrence timestamp.
    agg: dict[int, dict] = {}
    for s in subs:
        m = s.misconception
        if m is None:
            continue
        entry = agg.get(m.id)
        if entry is None:
            agg[m.id] = {
                "id": m.id,
                "code": m.code,
                "name": m.name,
                "concept": m.concept,
                "count": 1,
                "last_seen": s.created_at.isoformat() if s.created_at else None,
            }
        else:
            entry["count"] += 1

    log = sorted(agg.values(), key=lambda e: e["count"], reverse=True)
    return jsonify(misconceptions=log, total=sum(e["count"] for e in log))


@profile_bp.get("/recommendations")
@jwt_required()
def recommendations():
    """Next problems to attempt, targeting the student's weakest concepts."""
    user_id = int(get_jwt_identity())
    try:
        limit = min(max(int(request.args.get("limit", 6)), 1), 20)
    except (TypeError, ValueError):
        limit = 6
    return jsonify(recommendations=recommend(user_id, limit=limit))
