const STATUS_META = {
  passed: { label: "Passed", banner: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300", dot: "bg-emerald-400" },
  failed: { label: "Failed", banner: "border-rose-500/40 bg-rose-500/10 text-rose-300", dot: "bg-rose-400" },
  error: { label: "Error", banner: "border-amber-500/40 bg-amber-500/10 text-amber-300", dot: "bg-amber-400" },
  timeout: { label: "Timeout", banner: "border-amber-500/40 bg-amber-500/10 text-amber-300", dot: "bg-amber-400" },
};

export default function ResultsPanel({ results, submission }) {
  if (!results) return null;

  const overall = submission?.status || "failed";
  const meta = STATUS_META[overall] || STATUS_META.failed;
  const passed = submission?.passed_count ?? results.filter((r) => r.passed).length;
  const total = submission?.total_count ?? results.length;
  const pct = total ? Math.round((passed / total) * 100) : 0;

  return (
    <div className="mt-4 animate-rise">
      <div className={`rounded-xl border px-4 py-3 ${meta.banner}`}>
        <div className="flex items-center justify-between font-semibold">
          <span>{meta.label}</span>
          <span className="font-mono text-sm">{passed} / {total} passed</span>
        </div>
        <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-black/30">
          <div
            className="h-full rounded-full bg-current transition-all"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>

      <div className="mt-3 space-y-2">
        {results.map((r) => {
          const m = STATUS_META[r.status] || STATUS_META.failed;
          return (
            <div key={r.index} className="card p-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-ink">
                  Test {r.index + 1}
                  {r.is_hidden && (
                    <span className="ml-2 rounded bg-surface-2 px-1.5 py-0.5 font-mono text-xs text-faint">
                      hidden
                    </span>
                  )}
                </span>
                <span className="flex items-center gap-1.5 text-xs font-semibold">
                  <span className={`h-2 w-2 rounded-full ${m.dot}`} />
                  <span className="capitalize text-muted">{r.status}</span>
                </span>
              </div>

              {r.error && (
                <pre className="mt-2 overflow-x-auto whitespace-pre-wrap rounded-lg border border-rose-500/20 bg-rose-500/5 p-2 font-mono text-xs text-rose-300">
                  {r.error}
                </pre>
              )}

              {!r.is_hidden && !r.error && r.status !== "passed" && (
                <div className="mt-2 grid grid-cols-3 gap-2 text-xs">
                  <Field label="Input" value={r.input || "(none)"} />
                  <Field label="Expected" value={r.expected_output} />
                  <Field label="Your output" value={r.actual_output || "(empty)"} mismatch />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Field({ label, value, mismatch }) {
  return (
    <div>
      <span className="text-faint">{label}</span>
      <pre
        className={`mt-1 whitespace-pre-wrap rounded-lg p-1.5 font-mono ${
          mismatch ? "bg-rose-500/10 text-rose-300" : "bg-surface-2 text-ink"
        }`}
      >
        {value}
      </pre>
    </div>
  );
}
