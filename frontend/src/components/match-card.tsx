import type { Match } from "../lib/api-types";
import { formatKickoff, formatNumber } from "../lib/utils";
import { Badge } from "./ui/badge";
import { Card, CardContent } from "./ui/card";

function isChelsea(name: string): boolean {
  return name.toLowerCase().includes("chelsea");
}

export function MatchCard({ match }: { match: Match }) {
  const score = match.score;
  const chelseaHome = isChelsea(match.home.name);
  const chelseaWon =
    score !== null &&
    ((chelseaHome && score.home > score.away) || (!chelseaHome && score.away > score.home));
  const draw = score !== null && score.home === score.away;
  const top = [...match.player_stats]
    .filter((row) => row.rating !== null)
    .sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0))
    .slice(0, 4);

  return (
    <Card className="overflow-hidden transition duration-300 hover:-translate-y-0.5">
      <div className="h-1 bg-gradient-to-r from-chelsea-blue via-chelsea-gold to-chelsea-red" />
      <CardContent className="grid gap-6 pt-5 lg:grid-cols-[1.15fr_1fr]">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <Badge>{match.competition}</Badge>
            {match.matchday ? (
              <span className="text-xs text-muted-foreground">Matchday {match.matchday}</span>
            ) : null}
            <span className="text-xs text-muted-foreground">{formatKickoff(match.utc_kickoff)}</span>
          </div>
          <div className="mt-5 grid grid-cols-[1fr_auto_1fr] items-center gap-3">
            <TeamSide name={match.home.name} shortName={match.home.short_name} align="right" highlight={chelseaHome} />
            <div className="text-center">
              <p className="font-display text-5xl tabular-nums leading-none text-chelsea-gold sm:text-6xl">
                {score ? `${score.home}–${score.away}` : "—"}
              </p>
              <p className="mt-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                {score === null ? "No score" : chelseaWon ? "Chelsea win" : draw ? "Draw" : "Defeat"}
              </p>
            </div>
            <TeamSide name={match.away.name} shortName={match.away.short_name} align="left" highlight={!chelseaHome} />
          </div>
          {match.venue ? <p className="mt-4 text-center text-xs text-muted-foreground">{match.venue}</p> : null}
        </div>
        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
          <div>
            <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Events</p>
            <ul className="space-y-2 text-sm">
              {match.events.length === 0 ? (
                <li className="text-muted-foreground">No events mapped</li>
              ) : (
                match.events.map((event, index) => (
                  <li
                    key={`${event.minute}-${event.player_name}-${index}`}
                    className="flex gap-3 rounded-xl bg-muted/40 px-3 py-2"
                  >
                    <span className="w-8 shrink-0 tabular-nums text-chelsea-gold">{event.minute ?? "—"}′</span>
                    <span>
                      <span className="font-medium">{labelEvent(event.event_type)}</span> {event.player_name}
                      {event.detail ? (
                        <span className="block text-xs text-muted-foreground">{event.detail}</span>
                      ) : null}
                    </span>
                  </li>
                ))
              )}
            </ul>
          </div>
          <div>
            <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Key ratings
            </p>
            <ul className="space-y-2">
              {top.map((row) => (
                <li key={row.player.id} className="flex items-center justify-between gap-3 rounded-xl bg-muted/40 px-3 py-2">
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-medium">{row.player.name}</span>
                    <span className="text-xs text-muted-foreground">
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
        </div>
        <p className="text-[11px] text-muted-foreground lg:col-span-2">
          Sources: {match.sources.map((s) => `${s.source} (${s.score.toFixed(2)})`).join(" · ") || "unknown"}
        </p>
      </CardContent>
    </Card>
  );
}

function TeamSide({
  name,
  shortName,
  align,
  highlight,
}: {
  name: string;
  shortName: string | null;
  align: "left" | "right";
  highlight: boolean;
}) {
  return (
    <div className={align === "right" ? "text-right" : "text-left"}>
      <p className={`font-display text-2xl leading-none sm:text-3xl ${highlight ? "text-chelsea-blue dark:text-white" : "text-foreground"}`}>
        {shortName ?? name}
      </p>
      <p className="mt-1 truncate text-xs text-muted-foreground">{name}</p>
    </div>
  );
}

function labelEvent(eventType: string): string {
  switch (eventType) {
    case "GOAL":
      return "Goal";
    case "ASSIST":
      return "Assist";
    case "CARD":
      return "Card";
    case "SUBSTITUTION":
      return "Sub";
    case "OTHER":
      return "Event";
    default:
      return eventType;
  }
}
