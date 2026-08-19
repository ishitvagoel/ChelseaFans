import type { Match } from "../lib/api-types";
import { formatKickoff, formatNumber } from "../lib/utils";
import { Badge } from "./ui/badge";
import { Card, CardContent, CardHeader } from "./ui/card";

export function MatchCard({ match }: { match: Match }) {
  const score = match.score;
  const top = [...match.player_stats]
    .filter((row) => row.rating !== null)
    .sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0))
    .slice(0, 4);

  return (
    <Card className="transition hover:-translate-y-0.5">
      <CardHeader className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge>{match.competition}</Badge>
            {match.matchday ? (
              <span className="text-xs text-muted-foreground">MD {match.matchday}</span>
            ) : null}
          </div>
          <p className="mt-2 text-sm text-muted-foreground">{formatKickoff(match.utc_kickoff)}</p>
          <h3 className="mt-1 font-display text-2xl">
            {match.home.short_name ?? match.home.name}{" "}
            <span className="text-chelsea-gold">vs</span> {match.away.short_name ?? match.away.name}
          </h3>
          <p className="text-xs text-muted-foreground">{match.venue}</p>
        </div>
        <div className="text-right">
          <p className="font-display text-5xl tabular-nums leading-none text-chelsea-gold">
            {score ? `${score.home}–${score.away}` : "—"}
          </p>
        </div>
      </CardHeader>
      <CardContent className="grid gap-4 lg:grid-cols-2">
        <div>
          <p className="mb-2 text-xs uppercase tracking-wide text-muted-foreground">Events</p>
          <ul className="space-y-1 text-sm">
            {match.events.length === 0 ? (
              <li className="text-muted-foreground">No events mapped</li>
            ) : (
              match.events.map((event, index) => (
                <li key={`${event.minute}-${event.player_name}-${index}`}>
                  <span className="tabular-nums text-chelsea-gold">{event.minute ?? "—"}'</span>{" "}
                  <span className="font-medium">{event.event_type}</span> {event.player_name}
                  {event.detail ? <span className="text-muted-foreground"> · {event.detail}</span> : null}
                </li>
              ))
            )}
          </ul>
        </div>
        <div>
          <p className="mb-2 text-xs uppercase tracking-wide text-muted-foreground">Key ratings</p>
          <ul className="space-y-2">
            {top.map((row) => (
              <li key={row.player.id} className="flex items-center justify-between gap-3 text-sm">
                <span>
                  {row.player.name}
                  <span className="block text-xs text-muted-foreground">
                    {row.player.position ?? "Player"} · {formatNumber(row.minutes)}′
                  </span>
                </span>
                <span className="font-display text-2xl tabular-nums text-chelsea-gold">
                  {formatNumber(row.rating, 1)}
                </span>
              </li>
            ))}
          </ul>
        </div>
        <p className="text-[11px] text-muted-foreground lg:col-span-2">
          Sources: {match.sources.map((s) => `${s.source} (${s.score.toFixed(2)})`).join(" · ") || "unknown"}
        </p>
      </CardContent>
    </Card>
  );
}
