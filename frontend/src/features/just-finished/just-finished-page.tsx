import { useEffect, useState } from "react";

import { fetchContext, fetchJustFinished } from "../../lib/api";
import type { Match, TeamContext } from "../../lib/api-types";
import { MatchCard } from "../../components/match-card";
import { PageHero } from "../../components/page-hero";
import { PageLoader } from "../../components/page-loader";
import { ContextSkeleton } from "../../components/skeletons";
import { TeamContextCard } from "../../components/team-context-card";
import { useDemoMode } from "../../components/demo-mode";

export function JustFinishedPage() {
  const { demo, ready } = useDemoMode();
  const [matches, setMatches] = useState<Match[]>([]);
  const [context, setContext] = useState<TeamContext | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loadingMatches, setLoadingMatches] = useState(true);
  const [loadingContext, setLoadingContext] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoadingContext(true);
    void fetchContext()
      .then((next) => {
        if (!cancelled) setContext(next);
      })
      .catch(() => {
        if (!cancelled) setContext(null);
      })
      .finally(() => {
        if (!cancelled) setLoadingContext(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoadingMatches(true);
    setError(null);
    void fetchJustFinished(4)
      .then((nextMatches) => {
        if (!cancelled) setMatches(nextMatches);
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Failed to load");
      })
      .finally(() => {
        if (!cancelled) setLoadingMatches(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div className="page-wrap grid gap-5 py-5 sm:gap-6 sm:py-8 md:py-10">
      <PageHero kicker="Match centre" title="Just Finished">
        {demo
          ? "The last Chelsea results, with events and the ratings that mattered. Demo mode uses a curated sample so you can explore the product before connecting live keys."
          : "The last Chelsea results. Scores come from football-data.org; player ratings and events appear when API-Football's free tier covers the season (2022–2024)."}
      </PageHero>
      {loadingContext ? <ContextSkeleton /> : <TeamContextCard context={context} />}
      {loadingMatches ? (
        <PageLoader
          label={ready && !demo ? "Fetching live Chelsea results…" : "Loading match centre…"}
        />
      ) : null}
      {error ? (
        <p className="rounded-2xl border border-chelsea-red/40 bg-chelsea-red/10 p-4 text-sm">
          Could not reach the API ({error}). Start FastAPI on port 8000 or check the Vercel backend service.
        </p>
      ) : null}
      {!loadingMatches ? (
        <div className="grid gap-4">
          {matches.map((match) => (
            <MatchCard key={match.id} match={match} />
          ))}
          {matches.length === 0 && !error ? (
            <p className="text-sm text-muted-foreground">No finished matches available yet.</p>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
