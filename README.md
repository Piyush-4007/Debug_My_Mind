# DebugMyMind

**A Misconception-Aware Feedback System for Introductory Programming**

DebugMyMind is a web platform for intro-Python practice that explains the *why*
behind a wrong answer. Instead of "test failed," it diagnoses the specific
misconception behind a student's mistake, delivers a targeted micro-lesson,
tracks each student's weak spots over time, and gives teachers a class-level
view of where the cohort struggles.

> _Final Year Project · Group 07 — Piyush Singh · Vinit Pal · Ketan Bhendarkar_

---

## Monorepo Layout
| Path | What |
|------|------|
| `backend/`  | Flask REST API (auth, problems, models, seed) |
| `frontend/` | React 18 + Vite + Tailwind + Monaco app |
| `shared/`   | Docs, schemas, planning artifacts |

## Status
**Phase 1 — Foundation** (of 6). Auth + problem catalog + misconception catalog.
See [CLAUDE.md](CLAUDE.md) for the full roadmap and architecture.

---

## Quickstart

### Backend → http://localhost:5000
```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate          # Windows Git Bash  (.venv\Scripts\activate on cmd)
pip install -r requirements.txt
cp .env.example .env
flask --app app db-init                 # create tables
flask --app app seed                    # load starter data
python app.py
```

### Frontend → http://localhost:5173
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The frontend talks to the backend via `VITE_API_URL` (defaults to
`http://localhost:5000`).

## Database
Dev uses **SQLite** (no setup). Production uses **PostgreSQL** — the app reads
`DATABASE_URL`; if unset it falls back to `backend/dev.sqlite3`. Switching to
Postgres requires no code changes, only the env var.

## Deployment
Backend → Render · Frontend → Vercel. See the deployment guide in
`DebugMyMind_Project_Context.docx` (Section 7).

## License
Academic project — not yet licensed for redistribution.
