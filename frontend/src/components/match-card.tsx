import type { EventType, Match, MatchEvent, PlayerMatchStats } from "../lib/api-types";
import { formatKickoff, formatNumber } from "../lib/utils";
import { Badge } from "./ui/badge";
import { Card, CardContent } from "./ui/card";

function isChelsea(name: string): boolean {
  return name.toLowerCase().includes("chelsea");
}

function topRatedRows(stats: PlayerMatchStats[]): PlayerMatchStats[] {
  const rated = stats.filter((row) => row.rating !== null);
  if (rated.length > 0) {
    return [...rated].sort((a, b) => (b.rating ?? 0) - (a.rating ?? 0)).slice(0, 4);
  }
  return [...stats]
    .filter((row) => row.minutes !== null || row.goals !== null || row.assists !== null)
    .sort((a, b) => (b.goals ?? 0) - (a.goals ?? 0) || (b.minutes ?? 0) - (a.minutes ?? 0))
    .slice(0, 4);
}

export function MatchCard({ match }: { match: Match }) {
  const score = match.score;
  const chelseaHome = isChelsea(match.home.name);
  const chelseaWon =
    score !== null &&
    ((chelseaHome && score.home > score.away) || (!chelseaHome && score.away > score.home));
  const draw = score !== null && score.home === score.away;
  const resultLabel = score === null ? "No score" : chelseaWon ? "Win" : draw ? "Draw" : "Loss";
  const top = topRatedRows(match.player_stats);

  return (
    <Card className="overflow-hidden transition duration-300 md:hover:-translate-y-0.5">
      <div className="h-1 bg-gradient-to-r from-chelsea-blue via-chelsea-gold to-chelsea-red" />
      <CardContent className="pt-4 sm:pt-5">
        <div className="flex flex-wrap items-center gap-2">
          <Badge>{match.competition}</Badge>
          {match.matchday ? <span className="text-xs text-muted-foreground">MD {match.matchday}</span> : null}
          <span className="text-xs text-muted-foreground">{formatKickoff(match.utc_kickoff)}</span>
        </div>

        <div className="md:hidden">
          <PhoneScoreboard match={match} resultLabel={resultLabel} />
          <details className="mt-4 rounded-2xl bg-muted/35">
            <summary className="cursor-pointer list-none px-4 py-3 text-sm font-semibold">
              Events & ratings
            </summary>
            <div className="grid gap-4 px-4 pb-4">
              <EventList events={match.events} />
              <RatingList rows={top} totalCount={match.player_stats.length} />
            </div>
          </details>
        </div>

        <div className="mt-5 hidden grid-cols-[1.15fr_1fr] gap-6 md:grid lg:grid-cols-[1.2fr_1fr]">
          <div>
            <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-4">
              <TeamSide name={match.home.name} shortName={match.home.short_name} align="right" highlight={chelseaHome} />
              <div className="text-center">
                <p className="font-display text-6xl tabular-nums leading-none text-chelsea-gold">
                  {score ? `${score.home}–${score.away}` : "—"}
                </p>
                <p className="mt-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  {resultLabel === "Win" ? "Chelsea win" : resultLabel === "Loss" ? "Defeat" : resultLabel}
                </p>
              </div>
              <TeamSide name={match.away.name} shortName={match.away.short_name} align="left" highlight={!chelseaHome} />
            </div>
            {match.venue ? <p className="mt-4 text-center text-xs text-muted-foreground">{match.venue}</p> : null}
          </div>
          <div className="grid gap-5 xl:grid-cols-2">
            <EventList events={match.events} />
            <RatingList rows={top} totalCount={match.player_stats.length} />
          </div>
        </div>

        <p className="mt-4 text-[11px] text-muted-foreground">
          Sources: {match.sources.map((s) => `${s.source} (${s.score.toFixed(2)})`).join(" · ") || "unknown"}
        </p>
      </CardContent>
    </Card>
  );
}

function PhoneScoreboard({ match, resultLabel }: { match: Match; resultLabel: string }) {
  const score = match.score;
  return (
    <div className="mt-4 rounded-2xl bg-gradient-to-b from-chelsea-blue/40 to-transparent p-4">
      <div className="flex items-center justify-between gap-3 text-sm font-semibold">
        <span className="truncate">{match.home.short_name ?? match.home.name}</span>
        <span className="truncate text-right">{match.away.short_name ?? match.away.name}</span>
      </div>
      <p className="my-3 text-center font-display text-6xl tabular-nums leading-none text-chelsea-gold">
        {score ? `${score.home}–${score.away}` : "—"}
      </p>
      <p className="text-center text-[11px] font-semibold uppercase tracking-[0.18em] text-chelsea-gold">{resultLabel}</p>
      {match.venue ? <p className="mt-2 text-center text-xs text-muted-foreground">{match.venue}</p> : null}
    </div>
  );
}

function EventList({ events }: { events: MatchEvent[] }) {
  return (
    <div>
      <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Events</p>
      <ul className="space-y-2 text-sm">
        {events.length === 0 ? (
          <li className="text-muted-foreground">
            No events for this fixture on the free football-data.org tier. API-Football events cover seasons
            2022–2024 only.
          </li>
        ) : (
          events.map((event, index) => (
            <li
              key={`${event.minute}-${event.player_name}-${index}`}
              className="flex gap-3 rounded-xl bg-muted/40 px-3 py-2"
            >
              <span className="w-8 shrink-0 tabular-nums text-chelsea-gold">{event.minute ?? "—"}′</span>
              <span>
                <span className="font-medium">{labelEvent(event.event_type)}</span> {event.player_name}
                {event.detail ? <span className="block text-xs text-muted-foreground">{event.detail}</span> : null}
              </span>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

function RatingList({ rows, totalCount }: { rows: PlayerMatchStats[]; totalCount: number }) {
  return (
    <div>
      <p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Key ratings</p>
      <ul className="space-y-2">
        {rows.length === 0 ? (
          <li className="rounded-xl bg-muted/40 px-3 py-2 text-sm text-muted-foreground">
            {totalCount > 0
              ? "Player stats returned without ratings for this fixture."
              : "No player ratings for this fixture on the free API-Football tier (seasons 2022–2024 only)."}
          </li>
        ) : (
          rows.map((row) => (
            <li key={row.player.id} className="flex items-center justify-between gap-3 rounded-xl bg-muted/40 px-3 py-2">
              <span className="min-w-0">
                <span className="block truncate text-sm font-medium">{row.player.name}</span>
                <span className="text-xs text-muted-foreground">
                  {row.player.position ?? "Player"} · {formatNumber(row.minutes)}′
                  {row.goals ? ` · ${row.goals}G` : ""}
                </span>
              </span>
              <span className="font-display text-2xl tabular-nums text-chelsea-gold">
                {row.rating !== null ? formatNumber(row.rating, 1) : "—"}
              </span>
            </li>
          ))
        )}
      </ul>
    </div>
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
      <p
        className={`font-display text-3xl leading-none ${highlight ? "text-chelsea-blue dark:text-white" : "text-foreground"}`}
      >
        {shortName ?? name}
      </p>
      <p className="mt-1 truncate text-xs text-muted-foreground">{name}</p>
    </div>
  );
}

function labelEvent(eventType: EventType): string {
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
    default: {
      const _exhaustive: never = eventType;
      return _exhaustive;
    }
  }
}
