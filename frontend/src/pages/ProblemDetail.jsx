import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Editor from "@monaco-editor/react";
import api, { apiError } from "../api/client";
import Navbar from "../components/Navbar";
import ResultsPanel from "../components/ResultsPanel";
import DiagnosisCard from "../components/DiagnosisCard";
import SubmissionHistory from "../components/SubmissionHistory";

const DIFFICULTY = {
  easy: "text-emerald-300 bg-emerald-500/10 border-emerald-500/30",
  medium: "text-amber-300 bg-amber-500/10 border-amber-500/30",
  hard: "text-rose-300 bg-rose-500/10 border-rose-500/30",
};
const LANG_NAME = { python: "Python", java: "Java" };
const EXT = { python: "py", java: "java" };

export default function ProblemDetail() {
  const { slug } = useParams();
  const [problem, setProblem] = useState(null);
  const [codeByLang, setCodeByLang] = useState({});
  const [language, setLanguage] = useState("python");
  const [results, setResults] = useState(null);
  const [diagnosis, setDiagnosis] = useState(null);
  const [submission, setSubmission] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [historyKey, setHistoryKey] = useState(0);

  useEffect(() => {
    setLoading(true);
    setResults(null);
    setDiagnosis(null);
    api
      .get(`/api/problems/${slug}`)
      .then((res) => {
        const p = res.data.problem;
        setProblem(p);
        const langs = p.languages || ["python"];
        setLanguage(langs[0]);
        setCodeByLang({ ...(p.starter_codes || { python: p.starter_code }) });
      })
      .catch((err) => setError(apiError(err, "Failed to load problem")))
      .finally(() => setLoading(false));
  }, [slug]);

  const code = codeByLang[language] ?? "";
  const setCode = (val) => setCodeByLang((m) => ({ ...m, [language]: val ?? "" }));

  async function handleRun() {
    setSubmitting(true);
    setError("");
    setResults(null);
    setDiagnosis(null);
    try {
      const res = await api.post(`/api/problems/${slug}/submit`, { code, language });
      setResults(res.data.results);
      setDiagnosis(res.data.diagnosis);
      setSubmission(res.data.submission);
      setHistoryKey((k) => k + 1);
    } catch (err) {
      setError(apiError(err, "Submission failed"));
    } finally {
      setSubmitting(false);
    }
  }

  const languages = useMemo(() => problem?.languages || ["python"], [problem]);

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-6xl px-6 py-6">
        <Link to="/" className="text-sm font-medium text-violet-bright hover:underline">
          ← Back to catalog
        </Link>

        {loading && <p className="mt-6 text-muted">Loading…</p>}
        {error && !problem && <p className="mt-6 font-medium text-red-300">{error}</p>}

        {problem && (
          <div className="mt-4 grid animate-rise gap-6 lg:grid-cols-2">
            {/* Left: problem statement */}
            <section>
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="font-display text-3xl font-extrabold tracking-tight">
                  {problem.title}
                </h1>
                <span className="rounded-md bg-surface-2 px-2 py-0.5 font-mono text-xs capitalize text-muted">
                  {problem.concept}
                </span>
                <span
                  className={`rounded-md border px-2 py-0.5 text-xs font-semibold capitalize ${
                    DIFFICULTY[problem.difficulty] || "border-line text-muted"
                  }`}
                >
                  {problem.difficulty}
                </span>
              </div>

              <p className="mt-4 whitespace-pre-line leading-relaxed text-muted">
                {problem.description}
              </p>

              {problem.test_cases?.length > 0 && (
                <div className="mt-6">
                  <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-faint">
                    Example tests
                  </h2>
                  <div className="space-y-2">
                    {problem.test_cases.map((tc) => (
                      <div key={tc.id} className="card grid grid-cols-2 gap-3 p-3 text-sm">
                        <div>
                          <span className="text-xs font-semibold text-faint">Input</span>
                          <pre className="mt-1 whitespace-pre-wrap font-mono text-ink">
                            {tc.input || "(none)"}
                          </pre>
                        </div>
                        <div>
                          <span className="text-xs font-semibold text-faint">Expected</span>
                          <pre className="mt-1 whitespace-pre-wrap font-mono text-ink">
                            {tc.expected_output}
                          </pre>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <SubmissionHistory slug={slug} refreshKey={historyKey} />
            </section>

            {/* Right: editor + run + results */}
            <section>
              <div className="overflow-hidden rounded-xl border border-line">
                <div className="flex items-center justify-between border-b border-line bg-surface px-3 py-2">
                  {/* Language toggle */}
                  <div className="flex items-center gap-1 rounded-lg bg-bg-soft p-1">
                    {languages.map((lang) => (
                      <button
                        key={lang}
                        onClick={() => setLanguage(lang)}
                        className={`rounded-md px-3 py-1 text-xs font-semibold transition ${
                          language === lang
                            ? "bg-grad-violet text-white shadow"
                            : "text-muted hover:text-ink"
                        }`}
                      >
                        {LANG_NAME[lang] || lang}
                      </button>
                    ))}
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-faint">solution.{EXT[language]}</span>
                    <button
                      onClick={() => setCode(problem.starter_codes?.[language] || "")}
                      className="text-xs font-medium text-faint transition hover:text-ink"
                    >
                      Reset
                    </button>
                  </div>
                </div>
                <Editor
                  height="380px"
                  language={language === "java" ? "java" : "python"}
                  theme="vs-dark"
                  value={code}
                  onChange={(val) => setCode(val ?? "")}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    fontFamily: "JetBrains Mono, monospace",
                    scrollBeyondLastLine: false,
                    tabSize: 4,
                    padding: { top: 12 },
                  }}
                />
              </div>

              <div className="mt-3 flex items-center gap-3">
                <button
                  onClick={handleRun}
                  disabled={submitting || !code.trim()}
                  className="inline-flex items-center gap-2 rounded-lg bg-grad-violet px-5 py-2.5 font-semibold text-white shadow-lg transition hover:glow-violet disabled:opacity-60"
                >
                  {submitting ? "Running…" : `▶ Run ${LANG_NAME[language]}`}
                </button>
                {error && problem && (
                  <span className="text-sm font-medium text-red-300">{error}</span>
                )}
              </div>

              <ResultsPanel results={results} submission={submission} />
              <DiagnosisCard diagnosis={diagnosis} />
            </section>
          </div>
        )}
      </main>
    </div>
  );
}
