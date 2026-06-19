"""Problem bank: list / detail (any logged-in user) + CRUD (teacher only)."""
from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from extensions import db
from models import Problem, TestCase
from utils import slugify, teacher_required

problems_bp = Blueprint("problems", __name__, url_prefix="/api/problems")


@problems_bp.get("")
@jwt_required()
def list_problems():
    """List problems, optionally filtered by ?concept= or ?difficulty=."""
    query = Problem.query
    concept = request.args.get("concept")
    difficulty = request.args.get("difficulty")
    if concept:
        query = query.filter_by(concept=concept)
    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    problems = query.order_by(Problem.concept, Problem.difficulty, Problem.id).all()
    # List view: omit description/test cases for a lighter payload.
    return jsonify(
        problems=[
            {
                "id": p.id,
                "slug": p.slug,
                "title": p.title,
                "concept": p.concept,
                "difficulty": p.difficulty,
                "languages": p.languages or ["python"],
            }
            for p in problems
        ]
    )


@problems_bp.get("/<slug>")
@jwt_required()
def get_problem(slug: str):
    problem = Problem.query.filter_by(slug=slug).first()
    if problem is None:
        return jsonify(error="problem not found"), 404
    # Students see only visible test cases (examples).
    return jsonify(problem=problem.to_dict(include_hidden_tests=False))


@problems_bp.post("")
@teacher_required
def create_problem():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    concept = (data.get("concept") or "").strip().lower()

    if not title or not description or not concept:
        return jsonify(error="title, description and concept are required"), 400

    slug = data.get("slug") or slugify(title)
    if Problem.query.filter_by(slug=slug).first():
        return jsonify(error=f"slug '{slug}' already exists"), 409

    problem = Problem(
        slug=slug,
        title=title,
        description=description,
        concept=concept,
        difficulty=(data.get("difficulty") or "easy").strip().lower(),
        starter_code=data.get("starter_code") or "",
    )
    for i, tc in enumerate(data.get("test_cases") or []):
        problem.test_cases.append(
            TestCase(
                input=tc.get("input", ""),
                expected_output=tc.get("expected_output", ""),
                is_hidden=bool(tc.get("is_hidden", False)),
                ordering=tc.get("ordering", i),
            )
        )

    db.session.add(problem)
    db.session.commit()
    return jsonify(problem=problem.to_dict(include_hidden_tests=True)), 201


@problems_bp.delete("/<slug>")
@teacher_required
def delete_problem(slug: str):
    problem = Problem.query.filter_by(slug=slug).first()
    if problem is None:
        return jsonify(error="problem not found"), 404
    db.session.delete(problem)
    db.session.commit()
    return jsonify(deleted=slug), 200
