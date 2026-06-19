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
- `backend/runner`      sandboxed code execution        (Phase 2)
- `backend/diagnosis`   AST + ML + LLM hybrid engine     (Phase 3)
- `backend/profile`     misconception log + knowledge tracing (Phase 4)
- `backend/teacher`     class aggregation dashboards     (Phase 5)
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
**Phase 1 — Foundation.** Monorepo + schema + JWT auth + problem catalog +
starter misconception catalog. Backend serves problems; frontend lets a student
sign up, log in, and browse/view a problem.

### Roadmap (6 phases / ~6 months)
1. **Foundation** (wk 1–4) — *current*
2. **Submit + Grade** (wk 5–7) — Monaco editor, sandboxed runner, pass/fail
3. **Diagnosis Engine** (wk 8–12) — AST matchers + LLM + hybrid verifier (research core)
4. **Personalization** (wk 13–16) — misconception log, knowledge tracing, recommender
5. **Teacher Dashboard + Pilot** (wk 17–20) — aggregation views + user study
6. **Deployment + Paper** (wk 21–24) — Render/Vercel, IEEE paper, demo video

## Locked-in Decisions
- Language target: **Python** intro level. Java/C++ are v2 future work.
- LLM: **Gemini free tier** (prod), **Ollama** (dev). No paid Claude usage.
- Free-tier deploy (Render + Vercel) is acceptable for the pilot.
- Pilot: 20–40 first-year CSE volunteers, 3–4 week study.

## Forbidden Scope (until v2)
Multi-language support · real-time collab · mobile app · gamification.

## Team
- **Piyush Singh** — backend, diagnosis
- **Vinit Pal** — frontend, UX
- **Ketan Bhendarkar** — data, evaluation
