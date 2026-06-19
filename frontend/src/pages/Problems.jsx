import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/client";
import Navbar from "../components/Navbar";

const DIFFICULTY_STYLES = {
  easy: "bg-green-100 text-green-700",
  medium: "bg-amber-100 text-amber-700",
  hard: "bg-red-100 text-red-700",
};

export default function Problems() {
  const [problems, setProblems] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .get("/api/problems")
      .then((res) => setProblems(res.data.problems))
      .catch((err) => setError(err.response?.data?.error || "Failed to load problems"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="mx-auto max-w-5xl px-6 py-8">
        <h1 className="font-display text-3xl font-bold text-brand-maroon">Problem Catalog</h1>
        <p className="mt-1 text-brand-rose">
          Curated intro-Python problems, organised by concept.
        </p>

        {loading && <p className="mt-8 text-brand-rose">Loading problems…</p>}
        {error && <p className="mt-8 font-medium text-red-600">{error}</p>}

        <div className="mt-6 grid gap-3 sm:grid-cols-2">
          {problems.map((p) => (
            <Link
              key={p.id}
              to={`/problems/${p.slug}`}
              className="group rounded-xl border border-brand-pink/20 bg-white p-5 transition hover:border-brand-pink hover:shadow-md"
            >
              <div className="flex items-start justify-between gap-3">
                <h2 className="font-semibold text-brand-ink group-hover:text-brand-pink">
                  {p.title}
                </h2>
                <span
                  className={`shrink-0 rounded-full px-2 py-0.5 text-xs font-semibold capitalize ${
                    DIFFICULTY_STYLES[p.difficulty] || "bg-gray-100 text-gray-600"
                  }`}
                >
                  {p.difficulty}
                </span>
              </div>
              <span className="mt-2 inline-block rounded-md bg-brand-cream px-2 py-0.5 text-xs font-medium capitalize text-brand-rose">
                {p.concept}
              </span>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
