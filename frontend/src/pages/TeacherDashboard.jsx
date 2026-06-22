import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import api, { apiError } from "../api/client";
import Navbar from "../components/Navbar";
import { useAuth } from "../context/AuthContext";

function masteryColor(score) {
  if (score >= 0.85) return "var(--color-emerald, #6ee7b7)";
  if (score >= 0.5) return "var(--color-cyan, #67e8f9)";
  if (score >= 0.3) return "#fbbf24";
  return "#fb7185";
}

function pct(x) {
  return `${Math.round((x || 0) * 100)}%`;
}

export default function TeacherDashboard() {
  const { user } = useAuth();
  const [overview, setOverview] = useState(null);
  const [students, setStudents] = useState([]);
  const [detail, setDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  // Teachers only — students get bounced to their own dashboard.
  const notTeacher = user && user.role !== "teacher";

  useEffect(() => {
    if (notTeacher) return;
    Promise.all([api.get("/api/teacher/overview"), api.get("/api/teacher/students")])
      .then(([o, s]) => {
        setOverview(o.data);
        setStudents(s.data.students);
      })
      .catch((err) => setError(apiError(err, "Failed to load the class dashboard")))
      .finally(() => setLoading(false));
  }, [notTeacher]);

  function openStudent(id) {
    setDetailLoading(true);
    setDetail(null);
    api
      .get(`/api/teacher/students/${id}`)
      .then((res) => setDetail(res.data))
      .catch((err) => setError(apiError(err, "Failed to load student")))
      .finally(() => setDetailLoading(false));
  }

  if (notTeacher) return <Navigate to="/dashboard" replace />;

  const stats = overview?.stats;
  const concepts = overview?.concepts || [];
  const misconceptions = overview?.misconceptions || [];

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <header className="animate-rise">
          <span className="inline-flex items-center gap-2 rounded-full border border-violet/30 bg-violet/10 px-3 py-1 text-xs font-semibold text-violet-bright">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan" /> Teacher view
          </span>
          <h1 className="mt-4 font-display text-4xl font-extrabold tracking-tight sm:text-5xl">
            Class overview
          </h1>
          <p className="mt-2 max-w-2xl text-muted">
            Where the cohort is strong, where they're <span className="text-gradient font-semibold">stuck</span>,
            and which misconceptions show up most — aggregated across every student.
          </p>
        </header>

        {loading && <p className="mt-10 text-muted">Loading class data…</p>}
        {error && <p className="mt-10 font-medium text-red-300">{error}</p>}

        {!loading && !error && stats && (
          <>
            <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <Stat label="Students" value={stats.students} sub={`${stats.active_students} active`} />
              <Stat label="Submissions" value={stats.total_submissions} />
              <Stat label="Class accuracy" value={pct(stats.accuracy)} />
              <Stat label="Concepts" value={stats.concepts_tracked} />
            </div>

            <div className="mt-8 grid gap-6 lg:grid-cols-3">
              {/* Concept breakdown */}
              <section className="card animate-rise p-6 lg:col-span-2">
                <h2 className="font-display text-lg font-bold text-ink">Concept mastery (class average)</h2>
                <p className="mt-1 text-sm text-muted">Weakest concepts first — where the class needs the most help.</p>
                <div className="mt-5 space-y-4">
                  {concepts.length === 0 && <p className="text-sm text-muted">No data yet.</p>}
                  {concepts.map((c) => (
                    <div key={c.concept}>
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium capitalize text-ink">{c.concept}</span>
                        <span className="font-mono text-xs text-muted">
                          {pct(c.avg_mastery)} avg · {c.students_mastered}/{c.students_practicing} mastered
                        </span>
                      </div>
                      <div className="mt-1.5 h-2.5 overflow-hidden rounded-full bg-surface-2">
                        <div
                          className="h-full rounded-full transition-all duration-700"
                          style={{ width: `${Math.max(c.avg_mastery * 100, 3)}%`, background: masteryColor(c.avg_mastery) }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* Common misconceptions */}
              <section className="card animate-rise p-6">
                <h2 className="font-display text-lg font-bold text-ink">Top misconceptions</h2>
                <p className="mt-1 text-sm text-muted">Most frequent across the class.</p>
                {misconceptions.length === 0 ? (
                  <p className="mt-3 text-sm text-muted">None diagnosed yet.</p>
                ) : (
                  <ul className="mt-4 space-y-2.5">
                    {misconceptions.slice(0, 7).map((m) => (
                      <li key={m.id} className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-medium text-ink">{m.name}</p>
                          <p className="font-mono text-xs capitalize text-muted">
                            {m.concept} · {m.students_affected} student{m.students_affected === 1 ? "" : "s"}
                          </p>
                        </div>
                        <span className="shrink-0 rounded-md bg-surface-2 px-2 py-0.5 text-xs font-semibold text-muted">
                          ×{m.occurrences}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            </div>

            {/* Roster */}
            <section className="mt-8 animate-rise">
              <h2 className="font-display text-lg font-bold text-ink">Students</h2>
              <p className="mt-1 text-sm text-muted">Click a student to see their concept mastery and misconception log.</p>
              <div className="card mt-4 overflow-hidden">
                <div className="hidden grid-cols-12 gap-3 border-b border-line px-5 py-3 text-xs font-semibold uppercase tracking-wide text-faint sm:grid">
                  <span className="col-span-4">Name</span>
                  <span className="col-span-2 text-right">Attempts</span>
                  <span className="col-span-2 text-right">Accuracy</span>
                  <span className="col-span-4">Avg mastery</span>
                </div>
                {students.map((s) => (
                  <button
                    key={s.id}
                    onClick={() => openStudent(s.id)}
                    className="grid w-full grid-cols-12 items-center gap-3 border-b border-line/60 px-5 py-3 text-left text-sm transition last:border-0 hover:bg-surface-2"
                  >
                    <span className="col-span-12 font-medium text-ink sm:col-span-4">
                      {s.name}
                      {s.weak_spots.length > 0 && (
                        <span className="ml-2 hidden text-xs capitalize text-rose-300 sm:inline">
                          weak: {s.weak_spots.join(", ")}
                        </span>
                      )}
                    </span>
                    <span className="col-span-4 text-muted sm:col-span-2 sm:text-right">{s.attempts}</span>
                    <span className="col-span-4 text-muted sm:col-span-2 sm:text-right">{pct(s.accuracy)}</span>
                    <span className="col-span-4 sm:col-span-4">
                      <span className="flex items-center gap-2">
                        <span className="h-2 flex-1 overflow-hidden rounded-full bg-surface-2">
                          <span
                            className="block h-full rounded-full"
                            style={{ width: `${Math.max(s.avg_mastery * 100, 3)}%`, background: masteryColor(s.avg_mastery) }}
                          />
                        </span>
                        <span className="font-mono text-xs text-muted">{pct(s.avg_mastery)}</span>
                      </span>
                    </span>
                  </button>
                ))}
                {students.length === 0 && <p className="px-5 py-4 text-sm text-muted">No students yet.</p>}
              </div>
            </section>
          </>
        )}
      </main>

      {/* Student drilldown drawer */}
      {(detail || detailLoading) && (
        <div className="fixed inset-0 z-30 flex justify-end bg-black/50 backdrop-blur-sm" onClick={() => setDetail(null)}>
          <div
            className="h-full w-full max-w-md overflow-y-auto border-l border-line bg-bg p-6 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-start justify-between">
              <h3 className="font-display text-xl font-bold text-ink">
                {detailLoading ? "Loading…" : detail?.student.name}
              </h3>
              <button onClick={() => setDetail(null)} className="rounded-lg border border-line px-2 py-1 text-sm text-muted hover:text-ink">
                ✕
              </button>
            </div>
            {detail && (
              <>
                <p className="mt-1 text-sm text-muted">{detail.student.email}</p>
                <h4 className="mt-6 text-sm font-bold uppercase tracking-wide text-faint">Concept mastery</h4>
                <div className="mt-3 space-y-3">
                  {detail.concepts.length === 0 && <p className="text-sm text-muted">No attempts yet.</p>}
                  {detail.concepts.map((c) => (
                    <div key={c.concept}>
                      <div className="flex justify-between text-sm">
                        <span className="capitalize text-ink">{c.concept}</span>
                        <span className="font-mono text-xs text-muted">{pct(c.mastery_score)} · {c.correct}/{c.attempts}</span>
                      </div>
                      <div className="mt-1 h-2 overflow-hidden rounded-full bg-surface-2">
                        <div className="h-full rounded-full" style={{ width: `${Math.max(c.mastery_score * 100, 3)}%`, background: masteryColor(c.mastery_score) }} />
                      </div>
                    </div>
                  ))}
                </div>
                <h4 className="mt-6 text-sm font-bold uppercase tracking-wide text-faint">Misconception log</h4>
                {detail.misconceptions.length === 0 ? (
                  <p className="mt-2 text-sm text-muted">None diagnosed.</p>
                ) : (
                  <ul className="mt-3 space-y-2">
                    {detail.misconceptions.map((m) => (
                      <li key={m.id} className="flex justify-between gap-3 text-sm">
                        <span className="text-ink">{m.name}</span>
                        <span className="shrink-0 rounded-md bg-surface-2 px-2 py-0.5 text-xs font-semibold text-muted">×{m.count}</span>
                      </li>
                    ))}
                  </ul>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value, sub }) {
  return (
    <div className="card px-4 py-3">
      <p className="text-xs font-medium uppercase tracking-wide text-faint">{label}</p>
      <p className="mt-1 font-display text-2xl font-extrabold text-ink">{value}</p>
      {sub && <p className="text-xs text-muted">{sub}</p>}
    </div>
  );
}
