"""Cohort aggregation queries for the teacher dashboard.

All functions aggregate over users with role 'student' only. They read the
Phase 4 model (StudentProfile mastery + diagnosed Submissions) and roll it up to
class level. Pure read-only; no side effects.
"""
from __future__ import annotations

from sqlalchemy import case, func

from extensions import db
from models import Misconception, StudentProfile, Submission, User

# Keep in sync with profile.tracing.MASTERY_THRESHOLD.
from profile.tracing import MASTERY_THRESHOLD


def _student_ids() -> list[int]:
    return [u.id for u in User.query.filter_by(role="student").all()]


def class_overview() -> dict:
    """Headline class stats."""
    ids = _student_ids()
    n_students = len(ids)
    if not ids:
        return {
            "students": 0,
            "active_students": 0,
            "total_submissions": 0,
            "total_attempts": 0,
            "total_correct": 0,
            "accuracy": 0.0,
            "concepts_tracked": 0,
        }

    total_submissions = Submission.query.filter(Submission.user_id.in_(ids)).count()

    rows = (
        db.session.query(
            func.coalesce(func.sum(StudentProfile.attempts), 0),
            func.coalesce(func.sum(StudentProfile.correct), 0),
            func.count(func.distinct(StudentProfile.user_id)),
            func.count(func.distinct(StudentProfile.concept)),
        )
        .filter(StudentProfile.user_id.in_(ids))
        .one()
    )
    total_attempts, total_correct, active_students, concepts_tracked = rows

    return {
        "students": n_students,
        "active_students": int(active_students),
        "total_submissions": total_submissions,
        "total_attempts": int(total_attempts),
        "total_correct": int(total_correct),
        "accuracy": round(total_correct / total_attempts, 3) if total_attempts else 0.0,
        "concepts_tracked": int(concepts_tracked),
    }


def concept_breakdown() -> list[dict]:
    """Per-concept cohort mastery, weakest concept first."""
    ids = _student_ids()
    if not ids:
        return []

    rows = (
        db.session.query(
            StudentProfile.concept,
            func.avg(StudentProfile.mastery_score),
            func.count(StudentProfile.id),
            func.sum(StudentProfile.attempts),
            func.sum(StudentProfile.correct),
            func.sum(
                # mastered student count (1 when at/above threshold)
                case((StudentProfile.mastery_score >= MASTERY_THRESHOLD, 1), else_=0)
            ),
        )
        .filter(StudentProfile.user_id.in_(ids))
        .group_by(StudentProfile.concept)
        .all()
    )

    out = []
    for concept, avg_mastery, n_students, attempts, correct, mastered in rows:
        out.append(
            {
                "concept": concept,
                "avg_mastery": round(float(avg_mastery or 0.0), 4),
                "students_practicing": int(n_students),
                "students_mastered": int(mastered or 0),
                "attempts": int(attempts or 0),
                "correct": int(correct or 0),
                "accuracy": round(correct / attempts, 3) if attempts else 0.0,
            }
        )
    out.sort(key=lambda c: c["avg_mastery"])
    return out


def common_misconceptions(limit: int = 10) -> list[dict]:
    """Most frequent diagnosed misconceptions across the cohort."""
    ids = _student_ids()
    if not ids:
        return []

    rows = (
        db.session.query(
            Misconception.id,
            Misconception.code,
            Misconception.name,
            Misconception.concept,
            func.count(Submission.id),
            func.count(func.distinct(Submission.user_id)),
        )
        .join(Submission, Submission.misconception_id == Misconception.id)
        .filter(Submission.user_id.in_(ids))
        .group_by(Misconception.id)
        .order_by(func.count(Submission.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": mid,
            "code": code,
            "name": name,
            "concept": concept,
            "occurrences": int(occ),
            "students_affected": int(affected),
        }
        for mid, code, name, concept, occ, affected in rows
    ]


def student_roster() -> list[dict]:
    """One row per student: activity + average mastery + weak spots."""
    students = User.query.filter_by(role="student").order_by(User.name).all()
    roster = []
    for u in students:
        profiles = StudentProfile.query.filter_by(user_id=u.id).all()
        attempts = sum(p.attempts for p in profiles)
        correct = sum(p.correct for p in profiles)
        avg_mastery = (
            round(sum(p.mastery_score for p in profiles) / len(profiles), 4)
            if profiles
            else 0.0
        )
        weak = sorted(
            (p for p in profiles if p.mastery_score < MASTERY_THRESHOLD),
            key=lambda p: p.mastery_score,
        )
        roster.append(
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "concepts_tracked": len(profiles),
                "attempts": attempts,
                "correct": correct,
                "accuracy": round(correct / attempts, 3) if attempts else 0.0,
                "avg_mastery": avg_mastery,
                "weak_spots": [p.concept for p in weak[:3]],
            }
        )
    return roster


def student_detail(student_id: int) -> dict | None:
    """Per-student drilldown: concept mastery + misconception log."""
    u = db.session.get(User, student_id)
    if u is None or u.role != "student":
        return None

    profiles = (
        StudentProfile.query.filter_by(user_id=u.id)
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

    # Misconception log (aggregated by frequency), same shape as the student view.
    subs = (
        Submission.query.filter(
            Submission.user_id == u.id, Submission.misconception_id.isnot(None)
        )
        .order_by(Submission.created_at.desc())
        .all()
    )
    agg: dict[int, dict] = {}
    for s in subs:
        m = s.misconception
        if m is None:
            continue
        entry = agg.get(m.id)
        if entry is None:
            agg[m.id] = {
                "id": m.id,
                "name": m.name,
                "concept": m.concept,
                "count": 1,
            }
        else:
            entry["count"] += 1

    return {
        "student": {"id": u.id, "name": u.name, "email": u.email},
        "concepts": concepts,
        "misconceptions": sorted(agg.values(), key=lambda e: e["count"], reverse=True),
    }
