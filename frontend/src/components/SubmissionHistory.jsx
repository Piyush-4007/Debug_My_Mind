import { useEffect, useState } from "react";
import api from "../api/client";

const STATUS_STYLES = {
  passed: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300",
  failed: "border-rose-500/40 bg-rose-500/10 text-rose-300",
  error: "border-amber-500/40 bg-amber-500/10 text-amber-300",
  timeout: "border-amber-500/40 bg-amber-500/10 text-amber-300",
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
      <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-faint">
        Your attempts
      </h2>
      <div className="space-y-1.5">
        {subs.map((s) => (
          <div
            key={s.id}
            className="flex items-center justify-between rounded-lg border border-line bg-surface px-3 py-2 text-sm"
          >
            <span className="flex items-center gap-2 text-muted">
              <span className="font-mono text-xs text-faint">{s.language || "python"}</span>
              <span className="text-xs">{new Date(s.created_at).toLocaleString()}</span>
            </span>
            <span className="flex items-center gap-3">
              <span className="font-mono text-ink">
                {s.passed_count}/{s.total_count}
              </span>
              <span
                className={`rounded-full border px-2 py-0.5 text-xs font-semibold capitalize ${
                  STATUS_STYLES[s.status] || "border-line text-muted"
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
