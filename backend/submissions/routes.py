"""Submit code for grading + view submission history."""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from diagnosis import diagnose_submission
from extensions import db
from models import Problem, Submission
from runner import run_submission

submissions_bp = Blueprint("submissions", __name__, url_prefix="/api")

MAX_CODE_CHARS = 50_000


@submissions_bp.post("/problems/<slug>/submit")
@jwt_required()
def submit(slug: str):
    user_id = int(get_jwt_identity())
    problem = Problem.query.filter_by(slug=slug).first()
    if problem is None:
        return jsonify(error="problem not found"), 404

    data = request.get_json(silent=True) or {}
    code = data.get("code") or ""
    if not code.strip():
        return jsonify(error="code is required"), 400
    if len(code) > MAX_CODE_CHARS:
        return jsonify(error="code is too long"), 413
    if not problem.test_cases:
        return jsonify(error="this problem has no test cases yet"), 422

    outcome = run_submission(code, problem.test_cases)

    submission = Submission(
        user_id=user_id,
        problem_id=problem.id,
        code=code,
        status=outcome["status"],
        passed_count=outcome["passed_count"],
        total_count=outcome["total_count"],
    )

    # Phase 3: diagnose the misconception behind a failing submission.
    diagnosis = None
    if outcome["status"] != "passed":
        diagnosis = diagnose_submission(
            code,
            {"title": problem.title, "description": problem.description},
            outcome["results"],
        )
        # General-feedback diagnoses have no catalogued misconception.
        if diagnosis and diagnosis.get("misconception"):
            submission.misconception_id = diagnosis["misconception"]["id"]

    db.session.add(submission)
    db.session.commit()

    # Per-test results are returned live but not persisted in Phase 2.
    return (
        jsonify(
            submission=submission.to_dict(),
            results=outcome["results"],
            diagnosis=diagnosis,
        ),
        201,
    )


@submissions_bp.get("/submissions")
@jwt_required()
def list_submissions():
    """Current user's submissions, newest first. Filter with ?problem=<slug>."""
    user_id = int(get_jwt_identity())
    query = Submission.query.filter_by(user_id=user_id)

    slug = request.args.get("problem")
    if slug:
        problem = Problem.query.filter_by(slug=slug).first()
        if problem is None:
            return jsonify(submissions=[])
        query = query.filter_by(problem_id=problem.id)

    subs = query.order_by(Submission.created_at.desc()).limit(50).all()
    # History view: omit the (potentially large) code blob from the list.
    return jsonify(
        submissions=[
            {
                "id": s.id,
                "problem_id": s.problem_id,
                "status": s.status,
                "passed_count": s.passed_count,
                "total_count": s.total_count,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in subs
        ]
    )
