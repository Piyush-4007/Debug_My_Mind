"""Integration tests for the submit + history endpoints."""
import pytest

from extensions import db
from models import Problem, TestCase


@pytest.fixture()
def student_headers(client):
    res = client.post("/api/auth/signup", json={
        "name": "Stu", "email": "stu@example.com", "password": "secret1",
    })
    return {"Authorization": f"Bearer {res.get_json()['token']}"}


@pytest.fixture()
def seeded_problem(app):
    with app.app_context():
        p = Problem(
            slug="sum-to-n", title="Sum to N", description="d",
            concept="loops", difficulty="easy",
            starter_code="n = int(input())\n",
        )
        p.test_cases.append(TestCase(input="5\n", expected_output="15", ordering=0))
        p.test_cases.append(TestCase(input="3\n", expected_output="6", is_hidden=True, ordering=1))
        db.session.add(p)
        db.session.commit()
    return "sum-to-n"


def test_submit_correct_code(client, student_headers, seeded_problem):
    res = client.post(
        f"/api/problems/{seeded_problem}/submit",
        headers=student_headers,
        json={"code": "n = int(input())\nprint(sum(range(1, n + 1)))\n"},
    )
    assert res.status_code == 201
    body = res.get_json()
    assert body["submission"]["status"] == "passed"
    assert body["submission"]["passed_count"] == 2
    assert len(body["results"]) == 2


def test_submit_wrong_code(client, student_headers, seeded_problem):
    res = client.post(
        f"/api/problems/{seeded_problem}/submit",
        headers=student_headers,
        json={"code": "n = int(input())\nprint(sum(range(1, n)))\n"},
    )
    body = res.get_json()
    assert body["submission"]["status"] == "failed"
    assert body["submission"]["passed_count"] == 0


def test_submit_requires_code(client, student_headers, seeded_problem):
    res = client.post(
        f"/api/problems/{seeded_problem}/submit",
        headers=student_headers, json={"code": "   "},
    )
    assert res.status_code == 400


def test_submit_requires_auth(client, seeded_problem):
    res = client.post(f"/api/problems/{seeded_problem}/submit", json={"code": "print(1)"})
    assert res.status_code == 401


def test_history_lists_attempts(client, student_headers, seeded_problem):
    client.post(
        f"/api/problems/{seeded_problem}/submit",
        headers=student_headers,
        json={"code": "n = int(input())\nprint(sum(range(1, n + 1)))\n"},
    )
    res = client.get(f"/api/submissions?problem={seeded_problem}", headers=student_headers)
    assert res.status_code == 200
    subs = res.get_json()["submissions"]
    assert len(subs) == 1
    assert subs[0]["status"] == "passed"
    assert "code" not in subs[0]  # list view omits the code blob
