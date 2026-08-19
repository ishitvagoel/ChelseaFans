import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { fetchComparison, fetchContext, searchPlayers } from "../../lib/api";
import type { ComparisonResult, Player, TeamContext } from "../../lib/api-types";
import { PageHero } from "../../components/page-hero";
import { InlineLoader, PageLoader } from "../../components/page-loader";
import { TeamContextCard } from "../../components/team-context-card";
import { useDemoMode } from "../../components/demo-mode";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardHeader } from "../../components/ui/card";
import { formatNumber } from "../../lib/utils";

const PALETTE = ["#DBA111", "#6ea8ff", "#ED1C24", "#9ae6b4"];
const SEASONS = ["2022/23", "2023/24", "2024/25"] as const;
const LIVE_SEED_NAMES = ["palmer", "caicedo", "jackson", "neto", "colwill"];

export function ComparisonPage() {
  const [query, setQuery] = useState("");
  const [squad, setSquad] = useState<Player[]>([]);
  const [selected, setSelected] = useState<Player[]>([]);
  const [seasonFrom, setSeasonFrom] = useState("2023/24");
  const [seasonTo, setSeasonTo] = useState("2024/25");
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const [context, setContext] = useState<TeamContext | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { demo, ready } = useDemoMode();
  const [, setSeeded] = useState(false);
  const [loadingSquad, setLoadingSquad] = useState(true);
  const [loadingCompare, setLoadingCompare] = useState(false);

  useEffect(() => {
    void fetchContext()
      .then(setContext)
      .catch(() => setContext(null));
  }, []);

  useEffect(() => {
    if (!ready) return;
    let cancelled = false;
    setLoadingSquad(true);
    void searchPlayers("")
      .then((players) => {
        if (cancelled) return;
        setSquad(players);
        setSeeded((already) => {
          if (already || players.length === 0) return already;
          if (demo) {
            setSelected(
              players.filter((p) => ["demo-palmer", "demo-jackson", "demo-caicedo"].includes(p.id)),
            );
          } else {
            const live = players.filter((p) => p.id.startsWith("af-"));
            const seededLive = LIVE_SEED_NAMES.map((name) =>
              live.find((p) => p.name.toLowerCase().includes(name)),
            ).filter((p): p is Player => Boolean(p));
            setSelected(seededLive.length ? seededLive.slice(0, 3) : live.slice(0, 3));
          }
          return true;
        });
      })
      .catch(() => {
        if (!cancelled) setSquad([]);
      })
      .finally(() => {
        if (!cancelled) setLoadingSquad(false);
      });
    return () => {
      cancelled = true;
    };
  }, [demo, ready]);

  useEffect(() => {
    if (selected.length === 0) {
      setResult(null);
      setLoadingCompare(false);
      return;
    }
    let cancelled = false;
    setLoadingCompare(true);
    setError(null);
    void fetchComparison(
      selected.map((p) => p.id),
      seasonFrom,
      seasonTo,
    )
      .then((next) => {
        if (!cancelled) setResult(next);
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Compare failed");
      })
      .finally(() => {
        if (!cancelled) setLoadingCompare(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selected, seasonFrom, seasonTo]);

  const options = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return squad;
    return squad.filter(
      (player) => player.name.toLowerCase().includes(q) || player.id.toLowerCase().includes(q),
    );
  }, [query, squad]);

  const barData = useMemo(() => {
    if (!result) return [];
    return [
      {
        metric: "Goals",
        ...Object.fromEntries(result.players.map((p) => [p.player.name, p.season.goals ?? 0])),
      },
      {
        metric: "Assists",
        ...Object.fromEntries(result.players.map((p) => [p.player.name, p.season.assists ?? 0])),
      },
      {
        metric: "90s",
        ...Object.fromEntries(
          result.players.map((p) => [p.player.name, p.season.minutes ? Math.round(p.season.minutes / 90) : 0]),
        ),
      },
    ];
  }, [result]);

  function togglePlayer(player: Player) {
    setSelected((current) => {
      if (current.some((item) => item.id === player.id)) {
        return current.filter((item) => item.id !== player.id);
      }
      if (current.length >= 4) return current;
      return [...current, player];
    });
  }

  return (
    <div className="page-wrap grid gap-5 py-5 sm:gap-6 sm:py-8 md:py-10">
      <PageHero kicker="Historical lens" title="Player comparison">
        Choose 1–4 Chelsea players. Season filters apply to the left-hand metrics; career totals stay on the right.
        {demo
          ? " Sample players are pre-selected so the charts appear immediately."
          : " Live comparison uses API-Football free-tier seasons (2022–2024)."}
      </PageHero>
      <TeamContextCard context={context} />
      <Card>
        <CardHeader className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h2 className="font-display text-xl">Squad picker</h2>
            <p className="text-sm text-muted-foreground">{selected.length}/4 selected</p>
            {loadingSquad ? <InlineLoader label="Loading squad…" /> : null}
          </div>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="flex flex-col gap-3 lg:flex-row">
            <label className="sr-only" htmlFor="player-search">
              Search players
            </label>
            <input
              id="player-search"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search Palmer, Caicedo, Neto…"
              className="field-input flex-1"
            />
            <label className="flex items-center gap-2 text-xs text-muted-foreground">
              From
              <select
                value={seasonFrom}
                onChange={(event) => setSeasonFrom(event.target.value)}
                className="field-input w-full sm:w-32"
              >
                {SEASONS.map((season) => (
                  <option key={season}>{season}</option>
                ))}
              </select>
            </label>
            <label className="flex items-center gap-2 text-xs text-muted-foreground">
              To
              <select
                value={seasonTo}
                onChange={(event) => setSeasonTo(event.target.value)}
                className="field-input w-full sm:w-32"
              >
                {SEASONS.map((season) => (
                  <option key={season}>{season}</option>
                ))}
              </select>
            </label>
          </div>
          {selected.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {selected.map((player) => (
                <Button
                  key={`selected-${player.id}`}
                  type="button"
                  variant="gold"
                  size="sm"
                  className="min-h-11 md:min-h-8"
                  onClick={() => togglePlayer(player)}
                >
                  {player.name}
                  <span className="ml-1 opacity-70">×</span>
                </Button>
              ))}
            </div>
          ) : null}
          <div className="flex max-h-48 flex-wrap content-start gap-2 overflow-y-auto rounded-xl border border-border/50 p-2">
            {loadingSquad ? (
              <InlineLoader label="Fetching Chelsea squad…" />
            ) : options.length === 0 ? (
              <p className="p-2 text-sm text-muted-foreground">No players match that search.</p>
            ) : (
              options.map((player) => {
                const active = selected.some((item) => item.id === player.id);
                return (
                  <Button
                    key={player.id}
                    type="button"
                    variant={active ? "gold" : "outline"}
                    size="sm"
                    className="min-h-11 md:min-h-8"
                    aria-pressed={active}
                    onClick={() => togglePlayer(player)}
                  >
                    {player.shirt_number ? (
                      <span className="mr-1 opacity-70">{player.shirt_number}</span>
                    ) : null}
                    {player.name}
                  </Button>
                );
              })
            )}
          </div>
          {error ? <p className="text-sm text-chelsea-red">{error}</p> : null}
        </CardContent>
      </Card>

      {loadingCompare ? <PageLoader label="Loading player comparison…" /> : null}
      {!loadingCompare && selected.length === 0 ? (
        <Card>
          <CardContent className="pt-5 text-sm text-muted-foreground">
            Pick at least one player to render comparison charts.
          </CardContent>
        </Card>
      ) : null}
      {!loadingCompare && result && result.players.length > 0 ? (
        <>
      <div className="flex snap-x snap-mandatory gap-3 overflow-x-auto pb-2 [-ms-overflow-style:none] [scrollbar-width:none] md:grid md:grid-cols-2 md:overflow-visible md:pb-0 xl:grid-cols-4 [&::-webkit-scrollbar]:hidden">
        {result.players.map((item, index) => (
          <Card key={item.player.id} className="min-w-[82vw] snap-center overflow-hidden sm:min-w-[60vw] md:min-w-0">
            <div
              className="h-1"
              style={{ backgroundColor: PALETTE[index % PALETTE.length] }}
            />
            <CardHeader>
              <Badge>#{index + 1}</Badge>
              <h3 className="font-display text-2xl">{item.player.name}</h3>
              <p className="text-sm text-muted-foreground">
                {item.player.position ?? "Chelsea"} · {item.player.nationality}
              </p>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-3">
              <Metric label="Season G" value={formatNumber(item.season.goals)} />
              <Metric label="Career G" value={formatNumber(item.career.goals)} />
              <Metric label="Season A" value={formatNumber(item.season.assists)} />
              <Metric label="Career A" value={formatNumber(item.career.assists)} />
              <Metric label="Minutes" value={formatNumber(item.season.minutes)} />
              <Metric label="Rating" value={formatNumber(item.season.rating, 2)} />
              <Metric label="Prog. passes" value={formatNumber(item.season.progressive_passes)} />
              <Metric label="Prog. carries" value={formatNumber(item.season.progressive_carries)} />
            </CardContent>
          </Card>
        ))}
      </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <Card className="min-h-[280px]">
            <CardHeader>
              <h3 className="font-display text-xl">Season bars</h3>
            </CardHeader>
            <CardContent className="h-64 sm:h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(219,161,17,0.12)" />
                  <XAxis dataKey="metric" stroke="currentColor" tick={{ fontSize: 12 }} />
                  <YAxis stroke="currentColor" tick={{ fontSize: 12 }} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Legend />
                  {result.players.map((p, i) => (
                    <Bar
                      key={p.player.id}
                      dataKey={p.player.name}
                      fill={PALETTE[i % PALETTE.length]}
                      radius={[6, 6, 0, 0]}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          <Card className="hidden min-h-[320px] md:block">
            <CardHeader>
              <h3 className="font-display text-xl">Season radar</h3>
            </CardHeader>
            <CardContent className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart
                  data={[
                    {
                      metric: "Goals",
                      ...Object.fromEntries(result.players.map((p) => [p.player.name, p.season.goals ?? 0])),
                    },
                    {
                      metric: "Assists",
                      ...Object.fromEntries(result.players.map((p) => [p.player.name, p.season.assists ?? 0])),
                    },
                    {
                      metric: "Rating×10",
                      ...Object.fromEntries(
                        result.players.map((p) => [p.player.name, p.season.rating ? p.season.rating * 10 : 0]),
                      ),
                    },
                    {
                      metric: "Prog P /10",
                      ...Object.fromEntries(
                        result.players.map((p) => [
                          p.player.name,
                          p.season.progressive_passes ? p.season.progressive_passes / 10 : 0,
                        ]),
                      ),
                    },
                  ]}
                >
                  <PolarGrid stroke="rgba(219,161,17,0.25)" />
                  <PolarAngleAxis dataKey="metric" tick={{ fill: "currentColor", fontSize: 12 }} />
                  <PolarRadiusAxis tick={{ fill: "currentColor", fontSize: 10 }} />
                  {result.players.map((p, i) => (
                    <Radar
                      key={p.player.id}
                      name={p.player.name}
                      dataKey={p.player.name}
                      stroke={PALETTE[i % PALETTE.length]}
                      fill={PALETTE[i % PALETTE.length]}
                      fillOpacity={0.18}
                    />
                  ))}
                  <Legend />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
        </>
      ) : null}
    </div>
  );
}

const tooltipStyle = {
  background: "#0B1D36",
  border: "1px solid #DBA111",
  borderRadius: 12,
  color: "#fff8e7",
};

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">{label}</p>
      <p className="font-display text-2xl tabular-nums">{value}</p>
    </div>
  );
}

export default ComparisonPage;
