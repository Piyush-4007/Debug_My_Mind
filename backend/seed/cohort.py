"""Fabricate a demo class so the teacher dashboard has data to show.

Creates a handful of student accounts and, for each, synthesises per-concept
mastery rows (StudentProfile) plus a few graded submissions — including some
diagnosed misconceptions — without running any code through the runner. Idempotent:
re-running skips students that already exist.

Run with:  flask --app app seed-cohort
"""
from __future__ import annotations

import random

import click

from extensions import db
from models import Misconception, Problem, StudentProfile, Submission, User
from profile.tracing import bkt_update, BKT_PARAMS

COHORT = [
    "Aarav Mehta", "Diya Sharma", "Kabir Rao", "Ananya Iyer",
    "Rohan Gupta", "Saanvi Nair", "Vivaan Joshi", "Ishita Reddy",
]


def _student_email(name: str) -> str:
    return name.lower().split()[0] + "@class.dev"


def _simulate_mastery(rng: random.Random, n_attempts: int) -> tuple[float, int, int]:
    """Run BKT over a random correct/incorrect sequence; return (mastery, attempts, correct)."""
    # Each student has a latent skill that biases their success rate per concept.
    skill = rng.uniform(0.25, 0.9)
    mastery = BKT_PARAMS["p_init"]
    correct = 0
    for i in range(n_attempts):
        is_correct = rng.random() < skill
        prior = mastery if i > 0 else BKT_PARAMS["p_init"]
        mastery = bkt_update(prior, is_correct)
        correct += int(is_correct)
    return round(mastery, 4), n_attempts, correct


def run_cohort_seed() -> None:
    rng = random.Random(7)  # deterministic demo data

    problems = Problem.query.all()
    misconceptions = Misconception.query.all()
    if not problems or not misconceptions:
        click.echo("Run `seed` first — no problems/misconceptions to attach to.")
        return

    concepts = sorted({p.concept for p in problems})
    problems_by_concept: dict[str, list[Problem]] = {}
    for p in problems:
        problems_by_concept.setdefault(p.concept, []).append(p)
    misc_by_concept: dict[str, list[Misconception]] = {}
    for m in misconceptions:
        misc_by_concept.setdefault(m.concept, []).append(m)

    created = 0
    for name in COHORT:
        email = _student_email(name)
        if User.query.filter_by(email=email).first():
            continue

        student = User(name=name, email=email, role="student")
        student.set_password("password")
        db.session.add(student)
        db.session.flush()  # need student.id

        # Each student practises a random subset of concepts.
        practised = rng.sample(concepts, k=rng.randint(3, len(concepts)))
        for concept in practised:
            n_attempts = rng.randint(2, 8)
            mastery, attempts, correct = _simulate_mastery(rng, n_attempts)
            db.session.add(
                StudentProfile(
                    user_id=student.id,
                    concept=concept,
                    attempts=attempts,
                    correct=correct,
                    mastery_score=mastery,
                )
            )

            # Synthesise submissions: `correct` passes + (attempts-correct) fails.
            concept_problems = problems_by_concept.get(concept, [])
            if not concept_problems:
                continue
            for i in range(attempts):
                prob = rng.choice(concept_problems)
                passed = i < correct
                total = len(prob.test_cases) or 1
                sub = Submission(
                    user_id=student.id,
                    problem_id=prob.id,
                    code="# demo submission\n",
                    language="python",
                    status="passed" if passed else "failed",
                    passed_count=total if passed else 0,
                    total_count=total,
                )
                # Attach a plausible misconception to some failures.
                if not passed:
                    candidates = misc_by_concept.get(concept) or misconceptions
                    if rng.random() < 0.7:
                        sub.misconception_id = rng.choice(candidates).id
                db.session.add(sub)

        created += 1

    db.session.commit()
    click.echo(
        f"Seeded {created} demo student(s) into the cohort "
        f"(emails like aarav@class.dev, password 'password')."
        if created
        else "Demo cohort already present — nothing to add."
    )
