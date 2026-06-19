import { useState } from "react";

const CONFIDENCE_STYLES = {
  high: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300",
  medium: "border-amber-500/40 bg-amber-500/10 text-amber-300",
  low: "border-line bg-surface-2 text-muted",
  info: "border-cyan/40 bg-cyan/10 text-cyan",
};

export default function DiagnosisCard({ diagnosis }) {
  const [showLesson, setShowLesson] = useState(true);
  if (!diagnosis) return null;

  const { misconception, confidence, agreement, explanation, fix_hint } = diagnosis;
  const lesson = misconception?.lesson;
  const badgeStyle = CONFIDENCE_STYLES[confidence] || CONFIDENCE_STYLES.low;

  return (
    <div className="mt-4 animate-rise rounded-xl border border-violet/40 bg-violet/[0.06] p-5 glow-violet">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-display text-lg font-bold text-ink">
          🧠 Here&rsquo;s what we think went wrong
        </h3>
        <span
          className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize ${badgeStyle}`}
          title={
            confidence === "info"
              ? "No catalogued misconception matched — general AI feedback"
              : agreement
                ? "Rule-based analysis and the AI tutor agree"
                : "Single-source diagnosis — not yet cross-verified"
          }
        >
          {confidence === "info"
            ? "general feedback"
            : `${confidence} confidence${agreement ? " ✓" : ""}`}
        </span>
      </div>

      {misconception && (
        <div className="mt-3 flex flex-wrap items-center gap-2">
          <span className="font-semibold text-ink">{misconception.name}</span>
          <span className="rounded-md bg-surface-2 px-2 py-0.5 font-mono text-xs capitalize text-muted">
            {misconception.concept}
          </span>
        </div>
      )}

      <p className="mt-2 leading-relaxed text-muted">{explanation}</p>

      {fix_hint && (
        <p className="mt-3 rounded-lg border border-cyan/20 bg-cyan/5 px-3 py-2 text-sm text-cyan">
          <span className="font-semibold">Fix: </span>
          {fix_hint}
        </p>
      )}

      {lesson && (
        <div className="mt-4 border-t border-line pt-3">
          <button
            onClick={() => setShowLesson((s) => !s)}
            className="flex w-full items-center justify-between text-left text-sm font-semibold text-violet-bright"
          >
            <span>📘 Micro-lesson: {lesson.title}</span>
            <span>{showLesson ? "▲" : "▼"}</span>
          </button>

          {showLesson && (
            <div className="mt-2">
              <p className="whitespace-pre-line leading-relaxed text-muted">{lesson.content}</p>
              {lesson.worked_example && (
                <div className="mt-3">
                  <span className="text-xs font-semibold uppercase tracking-wide text-faint">
                    Worked example
                  </span>
                  <pre className="mt-1 overflow-x-auto rounded-lg border border-line bg-bg-soft p-3 font-mono text-sm text-emerald-200">
                    <code>{lesson.worked_example}</code>
                  </pre>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
