import { useState } from "react";

const CONFIDENCE_STYLES = {
  high: "bg-green-100 text-green-700",
  medium: "bg-amber-100 text-amber-700",
  low: "bg-gray-200 text-gray-600",
  info: "bg-blue-100 text-blue-700",
};

export default function DiagnosisCard({ diagnosis }) {
  const [showLesson, setShowLesson] = useState(true);
  if (!diagnosis) return null;

  const { misconception, confidence, agreement, explanation, fix_hint } = diagnosis;
  const lesson = misconception?.lesson;

  return (
    <div className="mt-4 rounded-xl border-2 border-brand-pink/40 bg-white p-5">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h3 className="font-display text-lg font-bold text-brand-maroon">
          🧠 Here&rsquo;s what we think went wrong
        </h3>
        <span
          className={`rounded-full px-2.5 py-0.5 text-xs font-semibold capitalize ${
            CONFIDENCE_STYLES[confidence] || CONFIDENCE_STYLES.low
          }`}
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
          <span className="font-semibold text-brand-ink">{misconception.name}</span>
          <span className="rounded-md bg-brand-cream px-2 py-0.5 text-xs font-medium capitalize text-brand-rose">
            {misconception.concept}
          </span>
        </div>
      )}

      <p className="mt-2 leading-relaxed text-brand-ink">{explanation}</p>

      {fix_hint && (
        <p className="mt-2 rounded-lg bg-brand-pink/5 px-3 py-2 text-sm text-brand-rose">
          <span className="font-semibold">Fix: </span>
          {fix_hint}
        </p>
      )}

      {lesson && (
        <div className="mt-4 border-t border-brand-pink/20 pt-3">
          <button
            onClick={() => setShowLesson((s) => !s)}
            className="flex w-full items-center justify-between text-left text-sm font-semibold text-brand-pink"
          >
            <span>📘 Micro-lesson: {lesson.title}</span>
            <span>{showLesson ? "▲" : "▼"}</span>
          </button>

          {showLesson && (
            <div className="mt-2">
              <p className="whitespace-pre-line leading-relaxed text-brand-ink">
                {lesson.content}
              </p>
              {lesson.worked_example && (
                <div className="mt-3">
                  <span className="text-xs font-semibold uppercase tracking-wide text-brand-rose">
                    Worked example
                  </span>
                  <pre className="mt-1 overflow-x-auto rounded-lg bg-brand-ink p-3 text-sm text-brand-cream">
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
