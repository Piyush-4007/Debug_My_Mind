"""Bayesian Knowledge Tracing (BKT) over per-concept student mastery.

Each `StudentProfile` row holds a running mastery estimate for one (student,
concept) pair. BKT models mastery as a hidden binary skill and updates the
probability the student "knows" the concept after every graded attempt, using
four parameters:

    p_init    P(L0)  prior probability the skill is already mastered
    p_transit P(T)   probability of learning the skill on an attempt
    p_slip    P(S)   probability of a wrong answer despite mastery
    p_guess   P(G)   probability of a right answer without mastery

Update for one observation (correct / incorrect):
    1. Bayesian condition on the evidence  -> posterior P(L | obs)
    2. Apply the learning transition        -> P(L_next) = post + (1-post)*P(T)

`record_attempt` is called from the submit endpoint after a submission is graded
and committed. It is defensive: any failure is swallowed so personalization can
never break grading.
"""
from __future__ import annotations

import logging

from extensions import db
from models import StudentProfile

log = logging.getLogger(__name__)

# Standard BKT priors. Tuned conservatively for an intro-programming pilot;
# revisit once the study yields labelled data (see CLAUDE.md, Phase 4 notes).
BKT_PARAMS = {
    "p_init": 0.10,
    "p_transit": 0.20,
    "p_slip": 0.10,
    "p_guess": 0.20,
}

# A concept is considered "mastered" at or above this posterior.
MASTERY_THRESHOLD = 0.85


def bkt_update(prior: float, correct: bool, params: dict | None = None) -> float:
    """Return the new mastery estimate after one observation.

    `prior` and the result are both P(skill mastered) in [0, 1].
    """
    p = params or BKT_PARAMS
    slip, guess, transit = p["p_slip"], p["p_guess"], p["p_transit"]

    prior = min(max(prior, 0.0), 1.0)

    if correct:
        num = prior * (1.0 - slip)
        denom = num + (1.0 - prior) * guess
    else:
        num = prior * slip
        denom = num + (1.0 - prior) * (1.0 - guess)

    posterior = num / denom if denom > 0 else prior
    # Learning transition: even a wrong attempt can teach the skill.
    return posterior + (1.0 - posterior) * transit


def record_attempt(user_id: int, concept: str, correct: bool) -> StudentProfile | None:
    """Upsert the (user, concept) profile row and advance its mastery via BKT.

    Returns the updated row, or None on any failure (never raises).
    """
    if not concept:
        return None
    try:
        profile = StudentProfile.query.filter_by(
            user_id=user_id, concept=concept
        ).first()
        if profile is None:
            profile = StudentProfile(
                user_id=user_id,
                concept=concept,
                attempts=0,
                correct=0,
                mastery_score=BKT_PARAMS["p_init"],
            )
            db.session.add(profile)

        profile.attempts = (profile.attempts or 0) + 1
        if correct:
            profile.correct = (profile.correct or 0) + 1

        prior = profile.mastery_score if profile.attempts > 1 else BKT_PARAMS["p_init"]
        profile.mastery_score = round(bkt_update(prior, correct), 4)

        db.session.commit()
        return profile
    except Exception as exc:  # personalization must never break grading
        log.warning("record_attempt failed (user=%s concept=%s): %s", user_id, concept, exc)
        db.session.rollback()
        return None
