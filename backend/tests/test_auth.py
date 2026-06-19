def test_health(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


def test_signup_login_me_flow(client):
    # signup
    res = client.post("/api/auth/signup", json={
        "name": "Asha", "email": "asha@example.com", "password": "secret1",
    })
    assert res.status_code == 201
    body = res.get_json()
    assert body["user"]["email"] == "asha@example.com"
    assert body["user"]["role"] == "student"
    token = body["token"]
    assert token

    # duplicate email rejected
    dup = client.post("/api/auth/signup", json={
        "name": "Asha2", "email": "asha@example.com", "password": "secret1",
    })
    assert dup.status_code == 409

    # login
    res = client.post("/api/auth/login", json={
        "email": "asha@example.com", "password": "secret1",
    })
    assert res.status_code == 200

    # wrong password
    bad = client.post("/api/auth/login", json={
        "email": "asha@example.com", "password": "nope",
    })
    assert bad.status_code == 401

    # /me with token
    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.get_json()["user"]["name"] == "Asha"

    # /me without token
    assert client.get("/api/auth/me").status_code == 401


def test_problems_require_auth_and_teacher_guard(client):
    # unauthenticated list -> 401
    assert client.get("/api/problems").status_code == 401

    # a student token cannot create problems
    student = client.post("/api/auth/signup", json={
        "name": "S", "email": "s@example.com", "password": "secret1", "role": "student",
    }).get_json()
    s_headers = {"Authorization": f"Bearer {student['token']}"}
    assert client.get("/api/problems", headers=s_headers).status_code == 200
    forbidden = client.post("/api/problems", headers=s_headers, json={
        "title": "X", "description": "d", "concept": "loops",
    })
    assert forbidden.status_code == 403

    # a teacher can
    teacher = client.post("/api/auth/signup", json={
        "name": "T", "email": "t@example.com", "password": "secret1", "role": "teacher",
    }).get_json()
    t_headers = {"Authorization": f"Bearer {teacher['token']}"}
    created = client.post("/api/problems", headers=t_headers, json={
        "title": "Sum to N", "description": "d", "concept": "loops",
        "test_cases": [{"input": "5\n", "expected_output": "15"}],
    })
    assert created.status_code == 201
    slug = created.get_json()["problem"]["slug"]
    assert slug == "sum-to-n"

    # detail visible to student, hidden tests excluded by default
    detail = client.get(f"/api/problems/{slug}", headers=s_headers)
    assert detail.status_code == 200
