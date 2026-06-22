import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api, { apiError } from "../api/client";
import Navbar from "../components/Navbar";
import { useAuth } from "../context/AuthContext";

const DIFFICULTY = {
  easy: "text-emerald-300 bg-emerald-500/10 border-emerald-500/30",
  medium: "text-amber-300 bg-amber-500/10 border-amber-500/30",
  hard: "text-rose-300 bg-rose-500/10 border-rose-500/30",
};

// Mastery band → bar colour. Low = needs work (rose), high = mastered (emerald).
function masteryColor(score) {
  if (score >= 0.85) return "var(--color-emerald, #6ee7b7)";
  if (score >= 0.5) return "var(--color-cyan, #67e8f9)";
  if (score >= 0.3) return "#fbbf24";
  return "#fb7185";
}

export default function Dashboard() {
  const { user } = useAuth();
  const [overview, setOverview] = useState(null);
  const [recs, setRecs] = useState([]);
  const [misconceptions, setMisconceptions] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/api/profile"),
      api.get("/api/profile/recommendations"),
      api.get("/api/profile/misconceptions"),
    ])
      .then(([o, r, m]) => {
        setOverview(o.data);
        setRecs(r.data.recommendations);
        setMisconceptions(m.data.misconceptions);
      })
      .catch((err) => setError(apiError(err, "Failed to load your dashboard")))
      .finally(() => setLoading(false));
  }, []);

  const stats = overview?.stats;
  const concepts = overview?.concepts || [];
  const hasData = concepts.length > 0;

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-6xl px-6 py-10">
        <header className="animate-rise">
          <span className="inline-flex items-center gap-2 rounded-full border border-violet/30 bg-violet/10 px-3 py-1 text-xs font-semibold text-violet-bright">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan" /> Your learning model
          </span>
          <h1 className="mt-4 font-display text-4xl font-extrabold tracking-tight sm:text-5xl">
            {user ? `${user.name.split(" ")[0]}'s progress` : "Progress"}
          </h1>
          <p className="mt-2 max-w-2xl text-muted">
            We track the <span className="text-gradient font-semibold">misconceptions</span> behind your
            mistakes and estimate how well you've mastered each concept — then point you at what to
            practise next.
          </p>
        </header>

        {loading && <p className="mt-10 text-muted">Loading your dashboard…</p>}
        {error && <p className="mt-10 font-medium text-red-300">{error}</p>}

        {!loading && !error && !hasData && (
          <div className="card mt-10 p-8 text-center">
            <p className="text-lg font-semibold text-ink">No attempts yet</p>
            <p className="mt-2 text-muted">
              Solve a few problems and your concept mastery, weak spots, and personalised
              recommendations will appear here.
            </p>
            <Link
              to="/"
              className="mt-5 inline-block rounded-xl bg-grad-violet px-5 py-2.5 font-semibold text-white shadow-lg transition hover:opacity-90"
            >
              Browse problems →
            </Link>
          </div>
        )}

        {!loading && !error && hasData && (
          <>
            {/* Stat strip */}
            <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <Stat label="Concepts tracked" value={stats.concepts_tracked} />
              <Stat label="Mastered" value={stats.concepts_mastered} sub={`of ${stats.concepts_tracked}`} />
              <Stat label="Attempts" value={stats.total_attempts} />
              <Stat label="Accuracy" value={`${Math.round(stats.accuracy * 100)}%`} />
            </div>

            <div className="mt-8 grid gap-6 lg:grid-cols-3">
              {/* Mastery bars */}
              <section className="card animate-rise p-6 lg:col-span-2">
                <h2 className="font-display text-lg font-bold text-ink">Concept mastery</h2>
                <p className="mt-1 text-sm text-muted">
                  Bayesian estimate of how well you know each concept (0–100%).
                </p>
                <div className="mt-5 space-y-4">
                  {concepts.map((c) => (
                    <div key={c.concept}>
                      <div className="flex items-center justify-between text-sm">
                        <span className="font-medium capitalize text-ink">
                          {c.concept}
                          {c.mastered && (
                            <span className="ml-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-emerald-300">
                              mastered
                            </span>
                          )}
                        </span>
                        <span className="font-mono text-xs text-muted">
                          {Math.round(c.mastery_score * 100)}% · {c.correct}/{c.attempts}
                        </span>
                      </div>
                      <div className="mt-1.5 h-2.5 overflow-hidden rounded-full bg-surface-2">
                        <div
                          className="h-full rounded-full transition-all duration-700"
                          style={{
                            width: `${Math.max(c.mastery_score * 100, 3)}%`,
                            background: masteryColor(c.mastery_score),
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </section>

              {/* Weak spots + misconception log */}
              <section className="card animate-rise p-6">
                <h2 className="font-display text-lg font-bold text-ink">Weak spots</h2>
                {overview.weak_spots.length === 0 ? (
                  <p className="mt-2 text-sm text-muted">None — you're on top of every concept you've practised. 🎉</p>
                ) : (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {overview.weak_spots.map((w) => (
                      <span
                        key={w}
                        className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-2.5 py-1 text-xs font-semibold capitalize text-rose-300"
                      >
                        {w}
                      </span>
                    ))}
                  </div>
                )}

                <h3 className="mt-6 font-display text-sm font-bold uppercase tracking-wide text-faint">
                  Misconception log
                </h3>
                {misconceptions.length === 0 ? (
                  <p className="mt-2 text-sm text-muted">No diagnosed misconceptions yet.</p>
                ) : (
                  <ul className="mt-3 space-y-2.5">
                    {misconceptions.slice(0, 6).map((m) => (
                      <li key={m.id} className="flex items-start justify-between gap-3">
                        <div>
                          <p className="text-sm font-medium text-ink">{m.name}</p>
                          <p className="font-mono text-xs capitalize text-muted">{m.concept}</p>
                        </div>
                        <span className="shrink-0 rounded-md bg-surface-2 px-2 py-0.5 text-xs font-semibold text-muted">
                          ×{m.count}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            </div>

            {/* Recommendations */}
            <section className="mt-8 animate-rise">
              <div className="flex items-end justify-between">
                <div>
                  <h2 className="font-display text-lg font-bold text-ink">Recommended for you</h2>
                  <p className="mt-1 text-sm text-muted">
                    Targeted at your weakest concepts, ramping gently in difficulty.
                  </p>
                </div>
              </div>
              <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {recs.map((r, i) => (
                  <Link
                    key={r.slug}
                    to={`/problems/${r.slug}`}
                    className="card card-hover group p-5"
                    style={{ animationDelay: `${Math.min(i * 40, 400)}ms` }}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-semibold text-ink transition group-hover:text-violet-bright">
                        {r.title}
                      </h3>
                      <span
                        className={`shrink-0 rounded-md border px-2 py-0.5 text-xs font-semibold capitalize ${
                          DIFFICULTY[r.difficulty] || "border-line text-muted"
                        }`}
                      >
                        {r.difficulty}
                      </span>
                    </div>
                    <p className="mt-2 text-xs text-muted">{r.reason}</p>
                    <div className="mt-3 flex items-center gap-2">
                      <span className="rounded-md bg-surface-2 px-2 py-0.5 font-mono text-xs capitalize text-muted">
                        {r.concept}
                      </span>
                      <span className="font-mono text-[10px] text-faint">
                        {Math.round(r.concept_mastery * 100)}% mastery
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          </>
        )}
      </main>
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
