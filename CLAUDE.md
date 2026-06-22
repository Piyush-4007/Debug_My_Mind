# DebugMyMind

> Single source of truth for any Claude Code / AI session on this repo.
> Claude Code does **not** see our planning chats — keep this file current.

## Project Summary
A misconception-aware feedback platform for introductory Python programming.
When a student submits wrong code, the system diagnoses the *misconception* behind
the error (not just "test failed"), serves a targeted micro-lesson, tracks each
student's weak spots over time, and gives teachers a class-level dashboard.

Final-year project (Group 07). Target: IEEE conference paper + live demo.

## Tech Stack
- **Frontend:** React 18, Vite, Monaco Editor, Tailwind CSS, Axios, Recharts
- **Backend:** Python (Flask), Flask-JWT-Extended, SQLAlchemy, PostgreSQL
- **Diagnosis (Phase 3+):** Python `ast`, scikit-learn / XGBoost, Gemini (prod) / Ollama (dev)
- **Deploy:** Render (backend + Postgres) + Vercel (frontend)

## Repo Layout (monorepo)
```
/backend     Flask REST API
/frontend    React + Vite app
/shared      docs, schemas, planning artifacts
```

### Backend modules
- `backend/auth`        JWT signup/login, role-based access (student/teacher)
- `backend/problems`    problem bank + test cases (CRUD)
- `backend/runner`      sandboxed code execution        (Phase 2 ✓)
- `backend/submissions` submit + grade + history         (Phase 2 ✓)
- `backend/diagnosis`   AST + LLM hybrid engine          (Phase 3 ✓)
- `backend/profile`     misconception log + knowledge tracing (Phase 4 ✓)
- `backend/teacher`     class aggregation dashboards     (Phase 5 ✓)
- `backend/models`      SQLAlchemy models (all 7 Phase-1 tables)
- `backend/seed`        starter problem bank + misconception catalog

## Database (Phase 1 schema)
`users · problems · test_cases · submissions · misconceptions · lessons · student_profiles`

**Dev uses SQLite** (zero setup); **prod uses Postgres**. Controlled by the
`DATABASE_URL` env var — code is identical for both. If `DATABASE_URL` is unset,
the app falls back to a local `backend/dev.sqlite3`.

## Local Dev Quickstart
```bash
# Backend  (http://localhost:5000)
cd backend
python -m venv .venv && source .venv/Scripts/activate   # Windows Git Bash
pip install -r requirements.txt
cp .env.example .env
flask --app app db-init      # create tables
flask --app app seed         # load starter problems + misconceptions
python app.py                # or: flask --app app run

# Frontend (http://localhost:5173)
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Conventions
- **Python:** black formatting, type hints on public functions, app-factory pattern.
- **React:** functional components + hooks only, Tailwind for all styling, no class components.
- **API:** REST, JSON, JWT in `Authorization: Bearer <token>` header. Routes under `/api`.
- **Commits:** conventional commits (`feat:`, `fix:`, `chore:`, `docs:`, ...).
- **Branches:** one feature branch per phase.

## Current Phase
**Phase 5 — Teacher Dashboard (DONE; pilot study is the team's non-code work).**
`backend/teacher` rolls the Phase-4 per-student model up to class level. Aggregation
(`aggregation.py`, students = users with role 'student' only): class overview
(students/active/submissions/accuracy), per-concept cohort mastery (avg + #
mastered, weakest first), most-common misconceptions (occurrences + students
affected), a student roster, and a per-student drilldown. Routes (`/api/teacher/*`,
all `@teacher_required`): `GET /overview`, `GET /students`, `GET /students/<id>`.
Frontend `/teacher` page (teacher-only; students redirected to `/dashboard`):
stat strip, cohort concept bars, top-misconceptions list, clickable student roster
with a slide-in drilldown drawer. Navbar shows "Class" for teachers, "Dashboard"
for students. Dev demo data: `flask --app app seed-cohort` fabricates 8 students
with synthesised mastery + diagnosed submissions (no runner needed; deterministic,
idempotent; emails like aarav@class.dev, pw 'password'). The actual **pilot user
study** (recruiting 20–40 students, 3–4 wk) is the team's research work, not code.
Next up: **Phase 6 — Deployment + Paper**.

### Phase 4 — Personalization (DONE)
`backend/profile` turns graded submissions
into a per-student learning model. `tracing.py` runs **Bayesian Knowledge Tracing**
(params p_init=.10, p_transit=.20, p_slip=.10, p_guess=.20; mastery threshold .85)
— the submit endpoint calls `record_attempt(user_id, problem.concept, correct)`
after grading, which upserts the `StudentProfile` row and advances `mastery_score`.
`recommender.py` ranks unsolved problems weakest-concept-first, gentler difficulty
first. Routes (`/api/profile`): `GET ""` (mastery per concept + stats + weak_spots),
`GET /misconceptions` (the student's diagnosed-misconception log, aggregated by
frequency), `GET /recommendations?limit=`. All personalization is defensive —
failures never block grading. Frontend adds a `/dashboard` page (mastery bars,
weak-spot chips, misconception log, recommended-problem cards) + Navbar links.
Next up: **Phase 5 — Teacher Dashboard + Pilot**.

### Phase 3 — Diagnosis Engine (DONE)
When a submission fails, the hybrid
engine (`backend/diagnosis`) names the misconception behind it and serves the
linked micro-lesson. Pipeline: `ast_analyzer` (structural patterns + runtime-
error signatures → candidate misconceptions with confidence) + `llm_client`
(Gemini `gemini-2.5-flash` via REST, structured JSON) + `verifier` (agreement →
high confidence; strong AST signal trusted; disagreement flagged). `engine`
looks up the `Misconception` by `code`, attaches its lesson, and the submit
endpoint stores `submission.misconception_id` and returns `diagnosis`. Frontend
shows a `DiagnosisCard` (confidence badge, explanation, fix hint, expandable
micro-lesson + worked example). Next up: **Phase 4 — Personalization**.

LLM notes: `GEMINI_API_KEY` + `GEMINI_MODEL` live in `backend/.env` (gitignored).
The LLM is never a hard dependency — any failure (no key, network, rate-limit,
bad JSON) falls back to AST-only diagnosis. `LLM_PROVIDER` switch leaves room
for Ollama in dev later. The ML-classifier vote from the original 3-way design
is deferred until the pilot yields labelled data (AST+LLM hybrid ships now).

Runner notes: each submission runs in an isolated `python -I` subprocess with a
5s wall-clock timeout per test. On Linux/Render it also applies RLIMIT_AS (256MB)
and RLIMIT_CPU via `preexec_fn`; on Windows dev the timeout is the only guard.
Output comparison is whitespace-forgiving. Hidden test values are never sent to
the client. Endpoints: `POST /api/problems/<slug>/submit`, `GET /api/submissions`.

### Roadmap (6 phases / ~6 months)
1. **Foundation** (wk 1–4) — done
2. **Submit + Grade** (wk 5–7) — done — Monaco editor, sandboxed runner, pass/fail
3. **Diagnosis Engine** (wk 8–12) — done — AST matchers + Gemini + hybrid verifier
4. **Personalization** (wk 13–16) — done — BKT knowledge tracing + misconception log + recommender
5. **Teacher Dashboard + Pilot** (wk 17–20) — dashboard done; pilot user study is team research work
6. **Deployment + Paper** (wk 21–24) — Render/Vercel, IEEE paper, demo video

## Locked-in Decisions
- Language target: **Python + Java** intro level (Java added in v3.2 — overrides the
  original "Python only" thesis scope). C++ remains future work.
- LLM: **Gemini free tier** (prod), **Ollama** (dev). No paid Claude usage.
- Free-tier deploy (Render + Vercel) is acceptable for the pilot.
- Pilot: 20–40 first-year CSE volunteers, 3–4 week study.

## Forbidden Scope (until v2)
C++ support · real-time collab · mobile app · gamification.
(Java multi-language shipped in v3.2.)

## v3.2 — Multi-language + Redesign
Problems are language-agnostic (stdin/stdout tests), solvable in **Python or Java**
via an editor toggle. `Problem.starter_code` (python) + `starter_code_java` +
`languages` JSON; `Submission.language`. Runner dispatches: python `-I` subprocess
or `javac`+`java -cp` (compile once, run each test). Diagnosis is language-aware —
AST matchers run for Python only; Java leans on the LLM (medium confidence). 20
seeded problems. Frontend rebuilt as a dark "code platform" (Inter/Sora/JetBrains
Mono, violet→cyan accents, hero catalog with search/filters, language toggle).
Known gap: catalogued micro-lesson *worked examples* are still Python even for Java
submissions (explanation itself is Java-aware).

## Team
- **Piyush Singh** — backend, diagnosis
- **Vinit Pal** — frontend, UX
- **Ketan Bhendarkar** — data, evaluation
