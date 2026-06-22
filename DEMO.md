# DebugMyMind — Demo Guide

A 6–8 minute live walkthrough that shows the three pillars: **misconception-aware
feedback** (student), **personalisation** (student dashboard), and the
**teacher class view**. Everything below uses genuine data produced by the real
pipeline — nothing is faked.

---

## 0. One-time setup (before the demo)

From `backend/` with the venv active:

```bash
flask --app app db-reset      # clean slate
flask --app app seed          # problem bank + misconceptions + demo accounts
flask --app app seed-demo     # Piyush / Vinit / Ketan — REAL graded submissions
flask --app app seed-cohort   # (optional) 8 extra students so the class looks full
```

Then start both servers (two terminals):

```bash
# terminal 1
cd backend && python app.py            # http://localhost:5000
# terminal 2
cd frontend && npm run dev             # http://localhost:5173
```

### Demo accounts (password = `password` for all)
| Who | Email | Use for |
|-----|-------|---------|
| Demo Student | `student@demo.dev` | the **live** student flow (starts empty on purpose) |
| Piyush Singh | `piyush@team.dev` | strong student — 90% accuracy |
| Vinit Pal | `vinit@team.dev` | improving — fixed an off-by-one and an index error |
| Ketan Bhendarkar | `ketan@team.dev` | struggling with recursion & strings |
| Demo Teacher | `teacher@demo.dev` | the **class dashboard** |

---

## 1. The hook — misconception-aware feedback (≈2 min)

Log in as **`student@demo.dev`**. Open the **Factorial** problem (recursion).

**Show the "wrong" path first** — paste a recursion with no base case:

```python
def fact(n):
    return n * fact(n - 1)

n = int(input())
print(fact(n))
```

Run it. → It fails, and the **Diagnosis Card** doesn't just say "test failed" — it
names the misconception (*"Recursion without a correct base case"*), explains the
*why*, gives a fix hint, and offers an expandable micro-lesson + worked example.
**This is the core research contribution — say that out loud.**

Now fix it and re-run to show the green pass:

```python
def fact(n):
    return 1 if n == 0 else n * fact(n - 1)

n = int(input())
print(fact(n))
```

> Optional second example (very relatable): open **Leap Year** and submit
> `print('YES' if y % 4 == 0 else 'NO')` — passes 2000, fails 1900.

---

## 2. Personalisation — the student dashboard (≈1.5 min)

Click **Dashboard** in the navbar (still as Demo Student).

Point out that the two attempts you *just* made already moved the model:
- **Concept mastery** bars — Bayesian Knowledge Tracing, updated per attempt.
- **Weak spots** — auto-surfaced.
- **Misconception log** — your diagnosed mistakes, aggregated.
- **Recommended for you** — next problems targeting your weakest concepts.

> Talking point: "Every submission updates a per-student mastery estimate, so the
> system knows what each learner is weak at — not just whether one test passed."

---

## 3. The teacher view — class dashboard (≈2.5 min)

Log out, log in as **`teacher@demo.dev`**, click **Class**.

Walk through top-to-bottom:
- **Stat strip** — students, submissions, class accuracy.
- **Concept mastery (class average)** — weakest concept first. Note which concept
  the *cohort* struggles with (recursion tends to be low).
- **Top misconceptions** — the most common thinking errors across the class, with
  how many students each one affected. These were really diagnosed by the engine.
- **Student roster** — click **Ketan Bhendarkar** to open the drilldown drawer:
  recursion mastery ~23% (0/2), and his real misconception log (missing base case,
  string immutability). Then click **Piyush** to contrast a strong student.

> Talking point: "A teacher sees, at a glance, that the class is weak on recursion
> and that 'missing base case' is the dominant misconception — so they know exactly
> what to reteach. That's the pedagogical payoff."

---

## 4. Close (≈30 sec)

One line on the architecture: *AST matchers + LLM, cross-checked by a verifier →
misconception → micro-lesson; submissions feed Bayesian Knowledge Tracing →
per-student model → class aggregation.* Mention Python **and** Java are supported.

---

## Reset between rehearsals

To wipe the live edits you made as Demo Student and start fresh:

```bash
flask --app app db-reset && flask --app app seed && flask --app app seed-demo
# add: flask --app app seed-cohort   (if you want the fuller class)
```

## Tips
- Keep the **wrong → diagnosis → fix → pass** arc tight; it's the money shot.
- If offline, that's fine: diagnosis falls back to the AST engine, which is what
  catches all the misconceptions in this script anyway (no API key needed).
- The hidden test values are never sent to the browser — safe to screen-share.
