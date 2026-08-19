import { useEffect, useState } from "react";

import { fetchContext, fetchJustFinished } from "../../lib/api";
import type { Match, TeamContext } from "../../lib/api-types";
import { MatchCard } from "../../components/match-card";
import { TeamContextCard } from "../../components/team-context-card";

export function JustFinishedPage() {
  const [matches, setMatches] = useState<Match[]>([]);
  const [context, setContext] = useState<TeamContext | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([fetchJustFinished(8), fetchContext()])
      .then(([nextMatches, nextContext]) => {
        setMatches(nextMatches);
        setContext(nextContext);
      })
      .catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Failed to load");
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8">
      <div>
        <p className="text-sm uppercase tracking-[0.2em] text-chelsea-gold">Recent results</p>
        <h1 className="font-display text-4xl sm:text-5xl">Just Finished</h1>
        <p className="mt-2 max-w-2xl text-muted-foreground">
          Last Chelsea matches with scores, events, and key player ratings — fused from multiple sources
          when keys are configured, otherwise demo data.
        </p>
      </div>
      <TeamContextCard context={context} />
      {loading ? <p className="text-muted-foreground">Loading matches…</p> : null}
      {error ? (
        <p className="rounded-xl border border-chelsea-red/40 bg-chelsea-red/10 p-4 text-sm">
          Could not reach the API ({error}). Start FastAPI on port 8000 or set VITE_API_BASE_URL.
        </p>
      ) : null}
      <div className="grid gap-4">
        {matches.map((match) => (
          <MatchCard key={match.id} match={match} />
        ))}
      </div>
    </div>
  );
}
