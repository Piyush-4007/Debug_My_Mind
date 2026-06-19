"""Idempotent seeding of the starter problem bank and misconception catalog.

Safe to run repeatedly: existing rows (matched by slug/code) are updated, new
ones inserted. Also creates a demo student and teacher account in dev.
"""
from __future__ import annotations

import click

from extensions import db
from models import Lesson, Misconception, Problem, TestCase, User
from .misconceptions_data import MISCONCEPTIONS
from .problems_data import PROBLEMS

DEMO_ACCOUNTS = [
    {"name": "Demo Student", "email": "student@demo.dev", "role": "student", "password": "password"},
    {"name": "Demo Teacher", "email": "teacher@demo.dev", "role": "teacher", "password": "password"},
]


def _seed_misconceptions() -> int:
    count = 0
    for entry in MISCONCEPTIONS:
        m = Misconception.query.filter_by(code=entry["code"]).first()
        if m is None:
            m = Misconception(code=entry["code"])
            db.session.add(m)
        m.name = entry["name"]
        m.concept = entry["concept"]
        m.description = entry["description"]
        m.example_wrong_code = entry["example_wrong_code"]

        lesson_data = entry["lesson"]
        if m.lesson is None:
            m.lesson = Lesson(
                title=lesson_data["title"],
                content=lesson_data["content"],
                worked_example=lesson_data.get("worked_example", ""),
            )
        else:
            m.lesson.title = lesson_data["title"]
            m.lesson.content = lesson_data["content"]
            m.lesson.worked_example = lesson_data.get("worked_example", "")
        count += 1
    return count


def _seed_problems() -> int:
    count = 0
    for entry in PROBLEMS:
        p = Problem.query.filter_by(slug=entry["slug"]).first()
        if p is None:
            p = Problem(slug=entry["slug"])
            db.session.add(p)
        p.title = entry["title"]
        p.description = entry["description"]
        p.concept = entry["concept"]
        p.difficulty = entry["difficulty"]
        p.starter_code = entry["starter_code"]

        # Replace test cases wholesale (keeps seeding deterministic).
        p.test_cases.clear()
        for i, tc in enumerate(entry["test_cases"]):
            p.test_cases.append(
                TestCase(
                    input=tc["input"],
                    expected_output=tc["expected_output"],
                    is_hidden=tc.get("is_hidden", False),
                    ordering=i,
                )
            )
        count += 1
    return count


def _seed_demo_accounts() -> int:
    count = 0
    for acc in DEMO_ACCOUNTS:
        if User.query.filter_by(email=acc["email"]).first():
            continue
        user = User(name=acc["name"], email=acc["email"], role=acc["role"])
        user.set_password(acc["password"])
        db.session.add(user)
        count += 1
    return count


def run_seed() -> None:
    n_misc = _seed_misconceptions()
    n_prob = _seed_problems()
    n_users = _seed_demo_accounts()
    db.session.commit()
    click.echo(
        f"Seeded {n_misc} misconceptions, {n_prob} problems, "
        f"{n_users} new demo account(s)."
    )
    if n_users:
        click.echo("  Demo logins (password = 'password'): "
                   "student@demo.dev / teacher@demo.dev")
