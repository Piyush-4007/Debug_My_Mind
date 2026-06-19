import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import api from "../api/client";
import Navbar from "../components/Navbar";

export default function ProblemDetail() {
  const { slug } = useParams();
  const [problem, setProblem] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    api
      .get(`/api/problems/${slug}`)
      .then((res) => setProblem(res.data.problem))
      .catch((err) => setError(err.response?.data?.error || "Failed to load problem"))
      .finally(() => setLoading(false));
  }, [slug]);

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-3xl px-6 py-8">
        <Link to="/" className="text-sm font-medium text-brand-pink hover:underline">
          ← Back to catalog
        </Link>

        {loading && <p className="mt-6 text-brand-rose">Loading…</p>}
        {error && <p className="mt-6 font-medium text-red-600">{error}</p>}

        {problem && (
          <>
            <div className="mt-3 flex flex-wrap items-center gap-3">
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

            <section className="mt-6 whitespace-pre-line leading-relaxed text-brand-ink">
              {problem.description}
            </section>

            <section className="mt-6">
              <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-rose">
                Starter code
              </h2>
              <pre className="overflow-x-auto rounded-xl bg-brand-ink p-4 text-sm text-brand-cream">
                <code>{problem.starter_code}</code>
              </pre>
            </section>

            {problem.test_cases?.length > 0 && (
              <section className="mt-6">
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
              </section>
            )}

            <p className="mt-8 rounded-lg border border-dashed border-brand-pink/40 bg-brand-pink/5 p-4 text-sm text-brand-rose">
              ✏️ The in-browser Monaco editor and “Run” button arrive in{" "}
              <strong>Phase 2 (Submit + Grade)</strong>. For now this is the read-only
              problem view.
            </p>
          </>
        )}
      </main>
    </div>
  );
}
