import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import api, { apiError } from "../api/client";
import Navbar from "../components/Navbar";
import { useAuth } from "../context/AuthContext";

const DIFFICULTY = {
  easy: "text-emerald-300 bg-emerald-500/10 border-emerald-500/30",
  medium: "text-amber-300 bg-amber-500/10 border-amber-500/30",
  hard: "text-rose-300 bg-rose-500/10 border-rose-500/30",
};

const LANG_LABEL = { python: "Py", java: "Java" };

export default function Problems() {
  const { user } = useAuth();
  const [problems, setProblems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [concept, setConcept] = useState("all");
  const [difficulty, setDifficulty] = useState("all");

  useEffect(() => {
    api
      .get("/api/problems")
      .then((res) => setProblems(res.data.problems))
      .catch((err) => setError(apiError(err, "Failed to load problems")))
      .finally(() => setLoading(false));
  }, []);

  const concepts = useMemo(
    () => ["all", ...Array.from(new Set(problems.map((p) => p.concept))).sort()],
    [problems]
  );

  const filtered = useMemo(
    () =>
      problems.filter(
        (p) =>
          (concept === "all" || p.concept === concept) &&
          (difficulty === "all" || p.difficulty === difficulty) &&
          p.title.toLowerCase().includes(query.toLowerCase())
      ),
    [problems, concept, difficulty, query]
  );

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-6xl px-6 py-10">
        {/* Hero */}
        <header className="animate-rise">
          <span className="inline-flex items-center gap-2 rounded-full border border-violet/30 bg-violet/10 px-3 py-1 text-xs font-semibold text-violet-bright">
            <span className="h-1.5 w-1.5 rounded-full bg-cyan" /> Python &amp; Java · misconception-aware
          </span>
          <h1 className="mt-4 font-display text-4xl font-extrabold tracking-tight sm:text-5xl">
            {user ? `Welcome back, ${user.name.split(" ")[0]}.` : "Problem Catalog"}
          </h1>
          <p className="mt-2 max-w-2xl text-muted">
            Pick a problem, write code in Python or Java, and get feedback that explains the{" "}
            <span className="text-gradient font-semibold">why</span> behind your mistakes — not just
            pass or fail.
          </p>
        </header>

        {/* Stat strip */}
        <div className="mt-8 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Stat label="Problems" value={problems.length} />
          <Stat label="Concepts" value={Math.max(concepts.length - 1, 0)} />
          <Stat label="Languages" value="2" sub="Python · Java" />
          <Stat label="Feedback" value="AI" sub="diagnosis engine" />
        </div>

        {/* Controls */}
        <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
          <div className="relative flex-1">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search problems…"
              className="w-full rounded-xl border border-line bg-surface px-4 py-2.5 text-ink outline-none transition focus:border-violet/60 focus:ring-2 focus:ring-violet/25"
            />
          </div>
          <Select value={difficulty} onChange={setDifficulty}
            options={["all", "easy", "medium", "hard"]} />
          <Select value={concept} onChange={setConcept} options={concepts} />
        </div>

        {loading && <p className="mt-10 text-muted">Loading problems…</p>}
        {error && <p className="mt-10 font-medium text-red-300">{error}</p>}
        {!loading && filtered.length === 0 && (
          <p className="mt-10 text-muted">No problems match your filters.</p>
        )}

        {/* Cards */}
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((p, i) => (
            <Link
              key={p.id}
              to={`/problems/${p.slug}`}
              className="card card-hover animate-rise group p-5"
              style={{ animationDelay: `${Math.min(i * 40, 400)}ms` }}
            >
              <div className="flex items-start justify-between gap-2">
                <h2 className="font-semibold text-ink transition group-hover:text-violet-bright">
                  {p.title}
                </h2>
                <span
                  className={`shrink-0 rounded-md border px-2 py-0.5 text-xs font-semibold capitalize ${
                    DIFFICULTY[p.difficulty] || "border-line text-muted"
                  }`}
                >
                  {p.difficulty}
                </span>
              </div>
              <div className="mt-3 flex items-center gap-2">
                <span className="rounded-md bg-surface-2 px-2 py-0.5 font-mono text-xs capitalize text-muted">
                  {p.concept}
                </span>
                <span className="flex-1" />
                {(p.languages || ["python"]).map((lang) => (
                  <span
                    key={lang}
                    className="rounded-md border border-line px-1.5 py-0.5 font-mono text-[10px] font-semibold uppercase tracking-wide"
                    style={{ color: lang === "java" ? "var(--color-java)" : "var(--color-py)" }}
                  >
                    {LANG_LABEL[lang] || lang}
                  </span>
                ))}
              </div>
            </Link>
          ))}
        </div>
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

function Select({ value, onChange, options }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="rounded-xl border border-line bg-surface px-3 py-2.5 capitalize text-ink outline-none transition focus:border-violet/60"
    >
      {options.map((o) => (
        <option key={o} value={o}>
          {o === "all" ? "All" : o}
        </option>
      ))}
    </select>
  );
}
