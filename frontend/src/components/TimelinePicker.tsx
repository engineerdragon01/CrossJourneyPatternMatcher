import { useState } from "react";
import { PRESETS } from "../presets";
import type { Event } from "../types";

interface Props {
  onSubmit: (timeline: Event[]) => void;
  loading: boolean;
}

export function TimelinePicker({ onSubmit, loading }: Props) {
  const [selected, setSelected] = useState<number | null>(null);
  const [customText, setCustomText] = useState("");

  function buildTimeline(): Event[] {
    const base = selected !== null ? [...PRESETS[selected].timeline] : [];
    if (!customText.trim()) return base;
    const extras: Event[] = customText
      .split("\n")
      .map((s) => s.trim())
      .filter(Boolean)
      .map((text, i) => ({
        day: base.length + i + 1,
        type: "symptom" as const,
        text,
        severity: 3,
      }));
    return [...base, ...extras];
  }

  const canSubmit = selected !== null || customText.trim().length > 0;

  return (
    <div className="view">
      <h1>CrossJourney Pattern Matcher</h1>
      <p className="subtitle">
        Pick a symptom pattern or describe your own. We'll find the most
        similar patient journeys and surface what they tried.
      </p>

      <h2>Choose a preset</h2>
      <div className="preset-grid">
        {PRESETS.map((preset, i) => (
          <div
            key={i}
            role="button"
            tabIndex={0}
            className={`preset-card ${selected === i ? "selected" : ""}`}
            onClick={() => setSelected(selected === i ? null : i)}
            onKeyDown={(e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                setSelected(selected === i ? null : i);
              }
            }}
          >
            <strong>{preset.label}</strong>
            <span>{preset.description}</span>
            <ul className="symptom-list">
              {preset.timeline.slice(0, 3).map((e, j) => (
                <li key={j}>{e.text}</li>
              ))}
              {preset.timeline.length > 3 && (
                <li className="more">+{preset.timeline.length - 3} more</li>
              )}
            </ul>
          </div>
        ))}
      </div>

      <h2>Add your own symptoms <span className="optional">(optional)</span></h2>
      <textarea
        className="symptom-editor"
        placeholder={"One symptom per line, e.g.:\nbrain fog · heavy\ncouldn't get off the couch"}
        value={customText}
        onChange={(e) => setCustomText(e.target.value)}
        rows={4}
      />

      <button
        className="btn-primary"
        disabled={!canSubmit || loading}
        onClick={() => onSubmit(buildTimeline())}
      >
        {loading ? "Searching…" : "Find similar journeys →"}
      </button>
    </div>
  );
}
