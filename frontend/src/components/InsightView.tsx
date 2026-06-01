import type { InsightResponse } from "../types";

interface Props {
  insight: InsightResponse;
  onReset: () => void;
}

function confidenceColor(confidence: string): string {
  const word = confidence.toLowerCase().split(/[\s—–]/)[0];
  if (word === "high") return "badge-high";
  if (word === "moderate") return "badge-moderate";
  return "badge-low";
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
      )}

      <div className="confidence-row">
        <span>Confidence:</span>
        <span className={`badge ${confidenceColor(insight.confidence)}`}>
          {insight.confidence}
        </span>
      </div>

      <button className="btn-ghost" onClick={onReset}>
        ← Start over
      </button>
    </div>
  );
}
