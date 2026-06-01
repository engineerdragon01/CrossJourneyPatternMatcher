import { useState } from "react";
import { fetchInsight, fetchMatches } from "./api";
import { DisclaimerBanner } from "./components/DisclaimerBanner";
import { InsightView } from "./components/InsightView";
import { MatchesView } from "./components/MatchesView";
import { TimelinePicker } from "./components/TimelinePicker";
import type { Event, InsightResponse, JourneyMatch } from "./types";

type View = "pick" | "matches" | "insight";

export function App() {
  const [view, setView] = useState<View>("pick");
  const [timeline, setTimeline] = useState<Event[]>([]);
  const [matches, setMatches] = useState<JourneyMatch[]>([]);
  const [insight, setInsight] = useState<InsightResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleTimelineSubmit(tl: Event[]) {
    setError(null);
    setLoading(true);
    setTimeline(tl);
    try {
      const res = await fetchMatches(tl);
      setMatches(res.matches);
      setView("matches");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  async function handleGetInsight() {
    setError(null);
    setLoading(true);
    try {
      const res = await fetchInsight(timeline);
      setInsight(res);
      setView("insight");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setLoading(false);
    }
  }

  function handleReset() {
    setView("pick");
    setTimeline([]);
    setMatches([]);
    setInsight(null);
    setError(null);
  }

  return (
    <>
      <DisclaimerBanner />
      <main className="container">
        {error && <div className="error-banner">{error}</div>}

        {view === "pick" && (
          <TimelinePicker onSubmit={handleTimelineSubmit} loading={loading} />
        )}
        {view === "matches" && (
          <MatchesView
            matches={matches}
            onGetInsight={handleGetInsight}
            onBack={handleReset}
            loading={loading}
          />
        )}
        {view === "insight" && insight && (
          <InsightView insight={insight} onReset={handleReset} />
        )}
      </main>
    </>
  );
}
