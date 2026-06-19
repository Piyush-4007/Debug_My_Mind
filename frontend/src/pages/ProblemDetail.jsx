import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Editor from "@monaco-editor/react";
import api, { apiError } from "../api/client";
import Navbar from "../components/Navbar";
import ResultsPanel from "../components/ResultsPanel";
import DiagnosisCard from "../components/DiagnosisCard";
import SubmissionHistory from "../components/SubmissionHistory";

export default function ProblemDetail() {
  const { slug } = useParams();
  const [problem, setProblem] = useState(null);
  const [code, setCode] = useState("");
  const [results, setResults] = useState(null);
  const [diagnosis, setDiagnosis] = useState(null);
  const [submission, setSubmission] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [historyKey, setHistoryKey] = useState(0); // bump to refresh history

  useEffect(() => {
    setLoading(true);
    setResults(null);
    setDiagnosis(null);
    api
      .get(`/api/problems/${slug}`)
      .then((res) => {
        setProblem(res.data.problem);
        setCode(res.data.problem.starter_code || "");
      })
      .catch((err) => setError(apiError(err, "Failed to load problem")))
      .finally(() => setLoading(false));
  }, [slug]);

  async function handleRun() {
    setSubmitting(true);
    setError("");
    setResults(null);
    setDiagnosis(null);
    try {
      const res = await api.post(`/api/problems/${slug}/submit`, { code });
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

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-6xl px-6 py-6">
        <Link to="/" className="text-sm font-medium text-brand-pink hover:underline">
          ← Back to catalog
        </Link>

        {loading && <p className="mt-6 text-brand-rose">Loading…</p>}
        {error && !problem && <p className="mt-6 font-medium text-red-600">{error}</p>}

        {problem && (
          <div className="mt-3 grid gap-6 lg:grid-cols-2">
            {/* Left: problem statement */}
            <section>
              <div className="flex flex-wrap items-center gap-3">
                <h1 className="font-display text-3xl font-bold text-brand-maroon">
                  {problem.title}
                </h1>
                <span className="rounded-md bg-brand-cream px-2 py-0.5 text-xs font-medium capitalize text-brand-rose">
                  {problem.concept}
                </span>
                <span className="rounded-full bg-brand-pink/10 px-2 py-0.5 text-xs font-semibold capitalize text-brand-pink">
                  {problem.difficulty}
                </span>
              </div>

              <p className="mt-4 whitespace-pre-line leading-relaxed text-brand-ink">
                {problem.description}
              </p>

              {problem.test_cases?.length > 0 && (
                <div className="mt-6">
                  <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-rose">
                    Example tests
                  </h2>
                  <div className="space-y-2">
                    {problem.test_cases.map((tc) => (
                      <div
                        key={tc.id}
                        className="grid grid-cols-2 gap-3 rounded-lg border border-brand-pink/20 bg-white p-3 text-sm"
                      >
                        <div>
                          <span className="text-xs font-semibold text-brand-rose">Input</span>
                          <pre className="mt-1 whitespace-pre-wrap text-brand-ink">
                            {tc.input || "(none)"}
                          </pre>
                        </div>
                        <div>
                          <span className="text-xs font-semibold text-brand-rose">Expected</span>
                          <pre className="mt-1 whitespace-pre-wrap text-brand-ink">
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
              <div className="overflow-hidden rounded-xl border border-brand-pink/30">
                <div className="flex items-center justify-between bg-brand-ink px-4 py-2">
                  <span className="text-xs font-semibold uppercase tracking-wide text-brand-cream/80">
                    solution.py
                  </span>
                  <button
                    onClick={() => setCode(problem.starter_code || "")}
                    className="text-xs font-medium text-brand-cream/70 hover:text-brand-cream"
                  >
                    Reset
                  </button>
                </div>
                <Editor
                  height="360px"
                  defaultLanguage="python"
                  theme="vs-dark"
                  value={code}
                  onChange={(val) => setCode(val ?? "")}
                  options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    scrollBeyondLastLine: false,
                    tabSize: 4,
                  }}
                />
              </div>

              <div className="mt-3 flex items-center gap-3">
                <button
                  onClick={handleRun}
                  disabled={submitting || !code.trim()}
                  className="rounded-lg bg-brand-maroon px-5 py-2.5 font-semibold text-white transition hover:bg-brand-pink disabled:opacity-60"
                >
                  {submitting ? "Running…" : "Run & Submit"}
                </button>
                {error && problem && (
                  <span className="text-sm font-medium text-red-600">{error}</span>
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
