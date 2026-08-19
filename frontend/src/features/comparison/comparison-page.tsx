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
import { TeamContextCard } from "../../components/team-context-card";
import { Badge } from "../../components/ui/badge";
import { Button } from "../../components/ui/button";
import { Card, CardContent, CardHeader } from "../../components/ui/card";
import { formatNumber } from "../../lib/utils";

const PALETTE = ["#DBA111", "#034694", "#ED1C24", "#8ab4f8"];

export function ComparisonPage() {
  const [query, setQuery] = useState("");
  const [options, setOptions] = useState<Player[]>([]);
  const [selected, setSelected] = useState<Player[]>([]);
  const [seasonFrom, setSeasonFrom] = useState("2023/24");
  const [seasonTo, setSeasonTo] = useState("2024/25");
  const [result, setResult] = useState<ComparisonResult | null>(null);
  const [context, setContext] = useState<TeamContext | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void fetchContext().then(setContext).catch(() => setContext(null));
  }, []);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      void searchPlayers(query)
        .then(setOptions)
        .catch(() => setOptions([]));
    }, 200);
    return () => window.clearTimeout(handle);
  }, [query]);

  useEffect(() => {
    if (selected.length === 0) {
      setResult(null);
      return;
    }
    void fetchComparison(
      selected.map((p) => p.id),
      seasonFrom,
      seasonTo,
    )
      .then(setResult)
      .catch((err: unknown) => setError(err instanceof Error ? err.message : "Compare failed"));
  }, [selected, seasonFrom, seasonTo]);

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
        metric: "Minutes / 90",
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
    <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8">
      <div>
        <p className="text-sm uppercase tracking-[0.2em] text-chelsea-gold">Historical lens</p>
        <h1 className="font-display text-4xl sm:text-5xl">Player comparison</h1>
        <p className="mt-2 max-w-2xl text-muted-foreground">
          Select 1–4 Chelsea players. Season filters apply to the left-hand metrics; career stays on the right.
        </p>
      </div>
      <TeamContextCard context={context} />
      <Card>
        <CardHeader>
          <h2 className="font-display text-xl">Squad picker</h2>
        </CardHeader>
        <CardContent className="grid gap-4">
          <div className="flex flex-col gap-3 sm:flex-row">
            <input
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="Search Palmer, Caicedo, Neto…"
              className="h-11 flex-1 rounded-xl border border-border bg-background px-3"
            />
            <select
              value={seasonFrom}
              onChange={(event) => setSeasonFrom(event.target.value)}
              className="h-11 rounded-xl border border-border bg-background px-3"
            >
              <option>2023/24</option>
              <option>2024/25</option>
            </select>
            <select
              value={seasonTo}
              onChange={(event) => setSeasonTo(event.target.value)}
              className="h-11 rounded-xl border border-border bg-background px-3"
            >
              <option>2023/24</option>
              <option>2024/25</option>
            </select>
          </div>
          <div className="flex flex-wrap gap-2">
            {options.map((player) => {
              const active = selected.some((item) => item.id === player.id);
              return (
                <Button
                  key={player.id}
                  variant={active ? "gold" : "outline"}
                  size="sm"
                  onClick={() => togglePlayer(player)}
                >
                  {player.name}
                </Button>
              );
            })}
          </div>
          {error ? <p className="text-sm text-chelsea-red">{error}</p> : null}
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {result?.players.map((item, index) => (
          <Card key={item.player.id}>
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
              <Metric label="Min" value={formatNumber(item.season.minutes)} />
              <Metric label="Rating" value={formatNumber(item.season.rating, 2)} />
              <Metric label="Prog. passes" value={formatNumber(item.season.progressive_passes)} />
              <Metric label="Prog. carries" value={formatNumber(item.season.progressive_carries)} />
            </CardContent>
          </Card>
        ))}
      </div>

      {result && result.players.length > 0 ? (
        <div className="grid gap-4 lg:grid-cols-2">
          <Card className="min-h-[320px]">
            <CardHeader>
              <h3 className="font-display text-xl">Season bars</h3>
            </CardHeader>
            <CardContent className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={barData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                  <XAxis dataKey="metric" stroke="currentColor" />
                  <YAxis stroke="currentColor" />
                  <Tooltip />
                  <Legend />
                  {result.players.map((p, i) => (
                    <Bar key={p.player.id} dataKey={p.player.name} fill={PALETTE[i % PALETTE.length]} />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
          <Card className="min-h-[320px]">
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
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" />
                  <PolarRadiusAxis />
                  {result.players.map((p, i) => (
                    <Radar
                      key={p.player.id}
                      name={p.player.name}
                      dataKey={p.player.name}
                      stroke={PALETTE[i % PALETTE.length]}
                      fill={PALETTE[i % PALETTE.length]}
                      fillOpacity={0.2}
                    />
                  ))}
                  <Legend />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>
      ) : (
        <p className="text-muted-foreground">Pick at least one player to render comparison charts.</p>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[11px] uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className="font-display text-2xl tabular-nums">{value}</p>
    </div>
  );
}

export default ComparisonPage;
