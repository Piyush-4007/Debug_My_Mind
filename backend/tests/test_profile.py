"""Tests for Phase 4 personalization: BKT math + profile endpoints."""
import pytest

from extensions import db
from models import Problem, TestCase
from profile.tracing import bkt_update, BKT_PARAMS, MASTERY_THRESHOLD


# --- BKT unit tests -------------------------------------------------------

def test_bkt_correct_raises_mastery():
    prior = BKT_PARAMS["p_init"]
    assert bkt_update(prior, correct=True) > prior


def test_bkt_incorrect_below_correct():
    prior = 0.5
    up = bkt_update(prior, correct=True)
    down = bkt_update(prior, correct=False)
    assert down < up


def test_bkt_stays_in_unit_interval():
    p = BKT_PARAMS["p_init"]
    for _ in range(30):
        p = bkt_update(p, correct=True)
        assert 0.0 <= p <= 1.0


def test_bkt_repeated_success_approaches_mastery():
    p = BKT_PARAMS["p_init"]
    for _ in range(8):
        p = bkt_update(p, correct=True)
    assert p >= MASTERY_THRESHOLD


# --- Endpoint integration tests ------------------------------------------

@pytest.fixture()
def student_headers(client):
    res = client.post("/api/auth/signup", json={
        "name": "Prof", "email": "prof@example.com", "password": "secret1",
    })
    return {"Authorization": f"Bearer {res.get_json()['token']}"}


@pytest.fixture()
def loop_problem(app):
    with app.app_context():
        p = Problem(
            slug="sum-to-n", title="Sum to N", description="d",
            concept="loops", difficulty="easy",
            starter_code="n = int(input())\n", languages=["python"],
        )
        p.test_cases.append(TestCase(input="5\n", expected_output="15", ordering=0))
        db.session.add(p)
        db.session.commit()
    return "sum-to-n"


def _submit(client, headers, slug, code):
    return client.post(f"/api/problems/{slug}/submit", headers=headers, json={"code": code})


def test_profile_empty_for_new_student(client, student_headers):
    res = client.get("/api/profile", headers=student_headers)
    assert res.status_code == 200
    body = res.get_json()
    assert body["concepts"] == []
    assert body["stats"]["concepts_tracked"] == 0


def test_passing_submission_updates_mastery(client, student_headers, loop_problem):
    _submit(client, student_headers, loop_problem,
            "n = int(input())\nprint(sum(range(1, n + 1)))\n")

    res = client.get("/api/profile", headers=student_headers)
    body = res.get_json()
    assert body["stats"]["concepts_tracked"] == 1
    loops = next(c for c in body["concepts"] if c["concept"] == "loops")
    assert loops["attempts"] == 1
    assert loops["correct"] == 1
    assert loops["mastery_score"] > BKT_PARAMS["p_init"]


def test_failing_submission_records_attempt_not_correct(client, student_headers, loop_problem):
    _submit(client, student_headers, loop_problem,
            "n = int(input())\nprint(sum(range(1, n)))\n")  # off by one

    res = client.get("/api/profile", headers=student_headers)
    loops = next(c for c in res.get_json()["concepts"] if c["concept"] == "loops")
    assert loops["attempts"] == 1
    assert loops["correct"] == 0


def test_recommendations_exclude_solved(client, student_headers, loop_problem):
    _submit(client, student_headers, loop_problem,
            "n = int(input())\nprint(sum(range(1, n + 1)))\n")

    res = client.get("/api/profile/recommendations", headers=student_headers)
    assert res.status_code == 200
    slugs = [r["slug"] for r in res.get_json()["recommendations"]]
    assert loop_problem not in slugs  # already solved


def test_misconception_log_requires_auth(client):
    assert client.get("/api/profile/misconceptions").status_code == 401
