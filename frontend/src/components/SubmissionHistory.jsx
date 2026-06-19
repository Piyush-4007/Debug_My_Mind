import { useEffect, useState } from "react";
import api from "../api/client";

const STATUS_STYLES = {
  passed: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
  error: "bg-amber-100 text-amber-800",
};

export default function SubmissionHistory({ slug, refreshKey }) {
  const [subs, setSubs] = useState([]);

  useEffect(() => {
    api
      .get(`/api/submissions?problem=${slug}`)
      .then((res) => setSubs(res.data.submissions))
      .catch(() => setSubs([]));
  }, [slug, refreshKey]);

  if (subs.length === 0) return null;

  return (
    <div className="mt-8">
      <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-brand-rose">
        Your attempts
      </h2>
      <div className="space-y-1.5">
        {subs.map((s) => (
          <div
            key={s.id}
            className="flex items-center justify-between rounded-lg border border-brand-pink/20 bg-white px-3 py-2 text-sm"
          >
            <span className="text-brand-rose">
              {new Date(s.created_at).toLocaleString()}
            </span>
            <span className="flex items-center gap-3">
              <span className="text-brand-ink">
                {s.passed_count}/{s.total_count}
              </span>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-semibold capitalize ${
                  STATUS_STYLES[s.status] || "bg-gray-100 text-gray-600"
                }`}
              >
                {s.status}
              </span>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
