# DebugMyMind — Full Guided Demo Script

A complete, step-by-step walkthrough. Every click, every paste, and exactly what
appears on screen. ~7 minutes. All data is genuine — produced by the real engine.

> Note on feedback text: this script assumes **no Gemini key** (offline / dev),
> which is the safe default for a live demo. In that mode the diagnosis card shows
> a **green "high confidence"** badge, the misconception name, an explanation, and
> the micro-lesson. (With a `GEMINI_API_KEY` set you additionally get a cyan
> "Fix:" hint line and a "✓" on the badge when the AI agrees — optional.)

---

## STEP 0 — Start the project (do this before the audience is watching)

Open **two terminals** in the project root.

**Terminal 1 — backend:**
```bash
cd backend
.venv/Scripts/activate          # Windows Git Bash;  (.venv\Scripts\activate on cmd/PowerShell)
# First time on this machine only — reset to clean demo data:
flask --app app db-reset
flask --app app seed             # problem bank + misconceptions + demo accounts
flask --app app seed-demo        # Piyush / Vinit / Ketan with REAL graded submissions
python app.py                    # serves http://localhost:5000  — leave running
```

**Terminal 2 — frontend:**
```bash
cd frontend
npm run dev                      # serves http://localhost:5173  — leave running
```

Open **http://localhost:5173** in the browser. You should see the login screen.
Keep DevTools closed and the window maximised.

> Optional: `flask --app app seed-cohort` adds 8 more students so the teacher
> class view looks fuller. For a focused demo you can skip it — the 3 named
> students already tell the story.

**All demo accounts use password: `password`**

| Email | Role | You use it to… |
|-------|------|----------------|
| `student@demo.dev` | student | run the live student flow (starts empty on purpose) |
| `teacher@demo.dev` | teacher | show the class dashboard |
| `ketan@team.dev` | student | (teacher view) the struggling student |
| `piyush@team.dev` | student | (teacher view) the strong student |
| `vinit@team.dev` | student | (teacher view) the improving student |

---

## ACT 1 — Misconception-aware feedback (the core idea) · ~2.5 min

### 1.1 Log in as the student
- On the login page, enter **`student@demo.dev`** / **`password`** → **Log in**.
- You land on the **Problems** catalog. Say: *"This is a student's practice view —
  20 problems, Python or Java, searchable by concept and difficulty."*

### 1.2 Open the Factorial problem
- Click the **Factorial** card (concept: recursion, Easy).
- Left side: the prompt + example tests. Right side: the Monaco code editor.

### 1.3 Submit WRONG code — recursion with no base case
- Clear the editor and paste **exactly**:
```python
def fact(n):
    return n * fact(n - 1)

n = int(input())
print(fact(n))
```
- Click **▶ Run Python**.

**What happens on screen:**
- The results panel shows the run **failed** (a `RecursionError` — the function
  never stops).
- The **🧠 "Here's what we think went wrong"** diagnosis card appears with:
  - A green **`high confidence`** badge (top-right).
  - Misconception: **"Recursion without a (correct) base case"** + a `recursion` tag.
  - Explanation: *"A recursive function that never hits a terminating condition
    recurses forever and raises RecursionError. Every recursion needs a base case
    reached before the recursive call."*
  - An expandable **📘 Micro-lesson: "Every recursion needs a base case"** (open by
    default) with a **Worked example**:
    ```python
    def fact(n):
        if n <= 1:        # base case
            return 1
        return n * fact(n - 1)
    ```

> **This is the money moment.** Say it out loud: *"Notice it didn't just say 'test
> failed' — it identified the **misconception** behind the bug and taught the fix.
> That diagnosis comes from our hybrid engine: AST rules + an LLM, cross-checked by
> a verifier."*

### 1.4 Fix it — show the green pass
- Replace the editor contents with the correct version:
```python
def fact(n):
    if n <= 1:
        return 1
    return n * fact(n - 1)

n = int(input())
print(fact(n))
```
- Click **▶ Run Python** → all tests **pass** (green). The expected answer for the
  visible test `5` is `120`.

### 1.5 (Optional) A second, very visual misconception — strings
- Click **← Back to catalog**, open **Reverse a String** (concept: strings).
- Paste:
```python
s = input()
r = s
for i in range(len(s)):
    r[i] = s[len(s) - 1 - i]
print(r)
```
- **▶ Run Python** → fails with a `TypeError`. Diagnosis card:
  **"Trying to mutate a string in place"** (high confidence), lesson **"Strings
  can't be edited in place"** with the `''.join(list(s))` worked example.
- Fix it live to show the pass (input `hello` → output `olleh`):
```python
print(input()[::-1])
```

> Avoid Leap Year as a "show the card" example — that wrong answer fails a test but
> doesn't map to a catalogued misconception, so **no card appears** (only 3/4 tests
> pass). Use Factorial / Reverse-String, which produce clear diagnoses.

---

## ACT 2 — Personalisation: the student dashboard · ~1.5 min

### 2.1 Open the dashboard
- In the top navbar, click **Dashboard**.

### 2.2 Walk through the four sections (all driven by what you just did)
- **Stat strip** — concepts tracked, mastered, attempts, accuracy. After Act 1 you'll
  see recursion (and strings) now tracked.
- **Concept mastery** bars — each concept has a Bayesian Knowledge Tracing score
  (0–100%). Say: *"Every attempt updates a per-student mastery estimate — recursion
  moved after those two tries."*
- **Weak spots** — concepts below the mastery threshold, surfaced automatically.
- **Misconception log** — the mistakes you were diagnosed with, by frequency.
- **Recommended for you** — next problems, chosen to target your weakest concepts,
  ramping gently in difficulty. Each card says *why* it was picked.

> Talking point: *"The system builds a model of what THIS learner is weak at — not
> just pass/fail. That model is what powers the recommendations."*

---

## ACT 3 — The teacher class view · ~2.5 min

### 3.1 Switch accounts
- Navbar → **Log out**.
- Log in as **`teacher@demo.dev`** / **`password`**.
- Note the navbar now shows **Class** (role-aware) instead of Dashboard.
- Click **Class**.

### 3.2 Walk top-to-bottom
- **Stat strip** — students, submissions, class-wide accuracy, concepts.
- **Concept mastery (class average)** — weakest concept first. **Recursion is the
  lowest** — say: *"At a glance the teacher sees the class is weakest on recursion."*
- **Top misconceptions** — the most common thinking errors across the class, each
  with how many students it affected. You'll see **"Recursion without a base case"**,
  **"Indexing past the end of a list"**, **"Trying to mutate a string in place"** —
  all genuinely diagnosed by the engine.

### 3.3 Drill into individual students
- In the **Students** table, click **Ketan Bhendarkar**. A side drawer slides in:
  - Concept mastery: **recursion ~23% (0/2)** — clearly his weak spot.
  - Misconception log: **"Recursion without a (correct) base case" ×2**, **"Trying
    to mutate a string in place" ×1**.
  - Say: *"The teacher can see Ketan specifically struggles with recursion and
    exactly which misconceptions to address."*
- Close the drawer (✕ or click outside). Now click **Piyush Singh** to contrast — a
  strong student (~90% accuracy, high mastery across concepts).

> Talking point: *"This is the pedagogical payoff — a teacher knows what to reteach
> to the whole class, AND can support individuals, without grading anything by hand."*

---

## CLOSE · ~30 sec

One-sentence architecture recap:
> *"A submission is graded in a sandbox, the diagnosis engine (AST rules + LLM,
> reconciled by a verifier) names the misconception and serves a micro-lesson, the
> result updates a Bayesian per-student mastery model, and that rolls up into the
> teacher's class dashboard. Python and Java are both supported."*

---

## Reset between rehearsals
To wipe the live edits you made as `student@demo.dev` and restore the clean story:
```bash
flask --app app db-reset && flask --app app seed && flask --app app seed-demo
# add  flask --app app seed-cohort  if you want the fuller class
```

## Safety / gotchas
- Hidden test values are never sent to the browser — safe to screen-share.
- Works fully offline; the AST engine catches every misconception in this script
  without any API key.
- If a page looks stale after switching accounts, refresh once (F5).
- The first `python` run per submission spawns a subprocess; a ~1s pause on Run is
  normal.
