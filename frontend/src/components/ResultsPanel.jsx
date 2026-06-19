const STATUS_META = {
  passed: { label: "Passed", banner: "bg-green-100 text-green-800 border-green-300", dot: "bg-green-500" },
  failed: { label: "Failed", banner: "bg-red-100 text-red-800 border-red-300", dot: "bg-red-500" },
  error: { label: "Error", banner: "bg-amber-100 text-amber-900 border-amber-300", dot: "bg-amber-500" },
  timeout: { label: "Timeout", banner: "bg-amber-100 text-amber-900 border-amber-300", dot: "bg-amber-500" },
};

export default function ResultsPanel({ results, submission }) {
  if (!results) return null;

  const overall = submission?.status || "failed";
  const meta = STATUS_META[overall] || STATUS_META.failed;
  const passed = submission?.passed_count ?? results.filter((r) => r.passed).length;
  const total = submission?.total_count ?? results.length;

  return (
    <div className="mt-4">
      <div className={`flex items-center justify-between rounded-lg border px-4 py-2.5 font-semibold ${meta.banner}`}>
        <span>{meta.label}</span>
        <span>
          {passed} / {total} tests passed
        </span>
      </div>

      <div className="mt-3 space-y-2">
        {results.map((r) => {
          const m = STATUS_META[r.status] || STATUS_META.failed;
          return (
            <div key={r.index} className="rounded-lg border border-brand-pink/20 bg-white p-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-brand-ink">
                  Test {r.index + 1}
                  {r.is_hidden && (
                    <span className="ml-2 rounded bg-gray-100 px-1.5 py-0.5 text-xs font-medium text-gray-500">
                      hidden
                    </span>
                  )}
                </span>
                <span className="flex items-center gap-1.5 text-xs font-semibold">
                  <span className={`h-2 w-2 rounded-full ${m.dot}`} />
                  <span className="capitalize">{r.status}</span>
                </span>
              </div>

              {r.error && (
                <pre className="mt-2 overflow-x-auto whitespace-pre-wrap rounded bg-red-50 p-2 text-xs text-red-700">
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
      <span className="text-brand-rose">{label}</span>
      <pre
        className={`mt-1 whitespace-pre-wrap rounded p-1.5 ${
          mismatch ? "bg-red-50 text-red-700" : "bg-brand-cream text-brand-ink"
        }`}
      >
        {value}
      </pre>
    </div>
  );
}
