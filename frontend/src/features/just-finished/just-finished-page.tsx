import { useEffect, useState } from "react";

import { fetchContext, fetchJustFinished } from "../../lib/api";
import type { Match, TeamContext } from "../../lib/api-types";
import { MatchCard } from "../../components/match-card";
import { PageHero } from "../../components/page-hero";
import { MatchListSkeleton } from "../../components/skeletons";
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
    <div className="page-wrap grid gap-6 py-8">
      <PageHero kicker="Match centre" title="Just Finished">
        The last Chelsea results, with events and the ratings that mattered. Demo mode uses a curated sample so you can
        explore the product before connecting live keys.
      </PageHero>
      <TeamContextCard context={loading ? null : context} />
      {loading ? <MatchListSkeleton /> : null}
      {error ? (
        <p className="rounded-2xl border border-chelsea-red/40 bg-chelsea-red/10 p-4 text-sm">
          Could not reach the API ({error}). Start FastAPI on port 8000 or check the Vercel backend service.
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
