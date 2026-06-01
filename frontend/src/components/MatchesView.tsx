import type { JourneyMatch } from "../types";

interface Props {
  matches: JourneyMatch[];
  onGetInsight: () => void;
  onBack: () => void;
  loading: boolean;
}

export function MatchesView({ matches, onGetInsight, onBack, loading }: Props) {
  return (
    <div className="view">
      <button className="btn-ghost" onClick={onBack}>
        ← Back
      </button>

      <h2>Most similar journeys</h2>
      <p className="subtitle">
        Found {matches.length} journeys with similar symptom patterns.
      </p>

      <div className="match-list">
        {matches.map((m) => (
          <div key={m.journey_id} className="card">
            <div className="match-header">
              <span className="condition-label">{m.condition}</span>
              <span className="journey-id">{m.journey_id}</span>
            </div>
            <div className="score-row">
              <div className="score-bar-track">
                <div
                  className="score-bar-fill"
                  style={{ width: `${Math.round(m.score * 100)}%` }}
                />
              </div>
              <span className="score-value">{(m.score * 100).toFixed(0)}% match</span>
            </div>
          </div>
        ))}
      </div>

      <button
        className="btn-primary"
        disabled={loading}
        onClick={onGetInsight}
      >
        {loading ? "Generating insight…" : "Get insight from these journeys →"}
      </button>
    </div>
  );
}
