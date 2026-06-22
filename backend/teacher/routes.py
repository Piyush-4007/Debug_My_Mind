"""Teacher-only class aggregation API (Phase 5)."""
from __future__ import annotations

from flask import Blueprint, jsonify

from utils import teacher_required
from . import aggregation

teacher_bp = Blueprint("teacher", __name__, url_prefix="/api/teacher")


@teacher_bp.get("/overview")
@teacher_required
def overview():
    return jsonify(
        stats=aggregation.class_overview(),
        concepts=aggregation.concept_breakdown(),
        misconceptions=aggregation.common_misconceptions(),
    )


@teacher_bp.get("/students")
@teacher_required
def students():
    return jsonify(students=aggregation.student_roster())


@teacher_bp.get("/students/<int:student_id>")
@teacher_required
def student(student_id: int):
    detail = aggregation.student_detail(student_id)
    if detail is None:
        return jsonify(error="student not found"), 404
    return jsonify(detail)
