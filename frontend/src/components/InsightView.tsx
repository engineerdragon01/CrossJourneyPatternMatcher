import type { InsightResponse } from "../types";

interface Props {
  insight: InsightResponse;
  onReset: () => void;
}

type ConfidenceLevel = "high" | "moderate" | "low";

function parseConfidence(confidence: string): { level: ConfidenceLevel; detail: string } {
  const word = confidence.toLowerCase().split(/[\s—–]/)[0];
  const level: ConfidenceLevel =
    word === "high" ? "high" : word === "moderate" ? "moderate" : "low";
  // Strip the leading word + separator so we show only the explanation
  const detail = confidence.replace(/^(high|moderate|low)\s*[—–-]?\s*/i, "").trim();
  return { level, detail };
}

export function InsightView({ insight, onReset }: Props) {
  return (
    <div className="view">
      <h2>Insight</h2>
      <p className="subtitle">
        Based on {insight.match_count} matched journeys from the synthetic cohort.
      </p>

      <div className="card">
        <h3>Summary</h3>
        <p>{insight.summary}</p>
      </div>

      {insight.patterns.length > 0 && (
        <div className="card">
          <h3>Patterns observed</h3>
          <ul className="pattern-list">
            {insight.patterns.map((p, i) => (
              <li key={i}>{p}</li>
            ))}
          </ul>
        </div>
      )}

      {insight.interventions_to_explore.length > 0 && (
        <div className="card">
          <h3>Interventions people explored</h3>
          <div className="intervention-table-wrap">
          <table className="intervention-table">
            <thead>
              <tr>
                <th>Intervention</th>
                <th>Cohort evidence</th>
                <th>Outcomes</th>
              </tr>
            </thead>
            <tbody>
              {insight.interventions_to_explore.map((iv, i) => (
                <tr key={i}>
                  <td><strong>{iv.name}</strong></td>
                  <td>{iv.cohort_evidence}</td>
                  <td>{iv.outcome_summary}</td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
        </div>
      )}

      <div className={`confidence-card confidence-${parseConfidence(insight.confidence).level}`}>
        <div className="confidence-header">
          <span className="confidence-label">Confidence</span>
          <span className={`confidence-chip confidence-chip-${parseConfidence(insight.confidence).level}`}>
            {parseConfidence(insight.confidence).level.toUpperCase()}
          </span>
        </div>
        {parseConfidence(insight.confidence).detail && (
          <p className="confidence-detail">{parseConfidence(insight.confidence).detail}</p>
        )}
      </div>

      <button className="btn-ghost" onClick={onReset}>
        ← Start over
      </button>
    </div>
  );
}
