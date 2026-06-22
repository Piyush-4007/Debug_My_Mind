"""Tests for Phase 5 teacher dashboard aggregation + auth guard."""
import pytest

from extensions import db
from models import Misconception, Problem, StudentProfile, Submission, User


@pytest.fixture()
def teacher_headers(client):
    res = client.post("/api/auth/signup", json={
        "name": "Teach", "email": "teach@example.com", "password": "secret1",
        "role": "teacher",
    })
    return {"Authorization": f"Bearer {res.get_json()['token']}"}


@pytest.fixture()
def student_headers(client):
    res = client.post("/api/auth/signup", json={
        "name": "Stu", "email": "stu@example.com", "password": "secret1",
    })
    return {"Authorization": f"Bearer {res.get_json()['token']}"}


@pytest.fixture()
def cohort(app):
    """Two students with mastery rows + a diagnosed submission."""
    with app.app_context():
        prob = Problem(
            slug="p1", title="P1", description="d", concept="loops",
            difficulty="easy", starter_code="",
        )
        misc = Misconception(code="off-by-one-range", name="Off by one",
                             concept="loops", description="d")
        db.session.add_all([prob, misc])
        db.session.flush()

        s1 = User(name="Alice", email="alice@s.dev", role="student")
        s1.set_password("password")
        s2 = User(name="Bob", email="bob@s.dev", role="student")
        s2.set_password("password")
        db.session.add_all([s1, s2])
        db.session.flush()

        db.session.add_all([
            StudentProfile(user_id=s1.id, concept="loops", attempts=4, correct=3, mastery_score=0.9),
            StudentProfile(user_id=s2.id, concept="loops", attempts=4, correct=1, mastery_score=0.3),
        ])
        db.session.add(Submission(
            user_id=s2.id, problem_id=prob.id, code="x", language="python",
            status="failed", passed_count=0, total_count=2, misconception_id=misc.id,
        ))
        db.session.commit()
        return {"s2_id": s2.id}


def test_teacher_routes_require_teacher_role(client, student_headers):
    assert client.get("/api/teacher/overview", headers=student_headers).status_code == 403
    assert client.get("/api/teacher/students", headers=student_headers).status_code == 403


def test_teacher_routes_require_auth(client):
    assert client.get("/api/teacher/overview").status_code == 401


def test_overview_aggregates_cohort(client, teacher_headers, cohort):
    res = client.get("/api/teacher/overview", headers=teacher_headers)
    assert res.status_code == 200
    body = res.get_json()
    # Alice + Bob are students (teacher excluded from student counts).
    assert body["stats"]["students"] == 2
    assert body["stats"]["total_attempts"] == 8
    assert body["stats"]["total_correct"] == 4

    loops = next(c for c in body["concepts"] if c["concept"] == "loops")
    assert loops["students_practicing"] == 2
    assert loops["students_mastered"] == 1  # only Alice >= 0.85

    codes = [m["code"] for m in body["misconceptions"]]
    assert "off-by-one-range" in codes


def test_student_roster_and_detail(client, teacher_headers, cohort):
    roster = client.get("/api/teacher/students", headers=teacher_headers).get_json()
    names = {s["name"] for s in roster["students"]}
    assert {"Alice", "Bob"} <= names

    detail = client.get(
        f"/api/teacher/students/{cohort['s2_id']}", headers=teacher_headers
    ).get_json()
    assert detail["student"]["name"] == "Bob"
    assert any(c["concept"] == "loops" for c in detail["concepts"])
    assert detail["misconceptions"][0]["count"] == 1


def test_student_detail_404_for_unknown(client, teacher_headers):
    assert client.get("/api/teacher/students/9999", headers=teacher_headers).status_code == 404
