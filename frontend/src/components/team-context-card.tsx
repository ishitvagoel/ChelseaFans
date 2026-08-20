import type { TeamContext } from "../lib/api-types";
import { formatNumber } from "../lib/utils";
import { Card, CardContent, CardHeader } from "./ui/card";
import { Badge } from "./ui/badge";

export function TeamContextCard({ context }: { context: TeamContext | null }) {
  if (!context) {
    return (
      <Card>
        <CardHeader>
          <h2 className="font-display text-xl">Premier League picture</h2>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">Standings unavailable.</CardContent>
      </Card>
    );
  }

  const form = (context.form ?? "").split("").filter(Boolean);
  const seasonNotStarted = context.played === 0;

  return (
    <Card>
      <CardHeader className="flex flex-row items-start justify-between gap-3">
        <div>
          <h2 className="font-display text-2xl">{context.team_name}</h2>
          <p className="text-sm text-muted-foreground">{context.competition}</p>
        </div>
        <Badge>{seasonNotStarted ? "Pre-season" : "Table"}</Badge>
      </CardHeader>
      {seasonNotStarted ? (
        <CardContent className="text-sm text-muted-foreground">
          The Premier League season has not started yet. Table position is a placeholder until matchday 1.
        </CardContent>
      ) : (
        <CardContent className="grid grid-cols-2 gap-4 overflow-x-auto sm:grid-cols-5">
          <Stat label="Pos" value={formatNumber(context.position)} />
          <Stat label="Pts" value={formatNumber(context.points)} />
          <Stat label="Pld" value={formatNumber(context.played)} />
          <Stat label="GD" value={formatNumber(context.goal_difference)} />
          <div className="col-span-2 sm:col-span-1">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">Form</p>
            <div className="mt-2 flex gap-1">
              {form.length === 0 ? (
                <span className="text-muted-foreground">—</span>
              ) : (
                form.map((result, index) => (
                  <span
                    key={`${result}-${index}`}
                    className={`flex h-8 w-8 items-center justify-center rounded-full text-xs font-bold ${formClass(result)}`}
                  >
                    {result}
                  </span>
                ))
              )}
            </div>
          </div>
        </CardContent>
      )}
    </Card>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">{label}</p>
      <p className="font-display text-3xl tabular-nums">{value}</p>
    </div>
  );
}

function formClass(result: string): string {
  switch (result) {
    case "W":
      return "bg-emerald-500/20 text-emerald-300";
    case "D":
      return "bg-chelsea-gold/20 text-chelsea-gold";
    case "L":
      return "bg-chelsea-red/20 text-red-300";
    default:
      return "bg-muted text-muted-foreground";
  }
}
