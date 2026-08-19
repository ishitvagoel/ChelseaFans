import { useDemoMode } from "./demo-mode";

export function AppFooter() {
  const { demo } = useDemoMode();
  return (
    <footer className="mt-auto hidden border-t border-border/60 py-8 md:block">
      <div className="page-wrap flex flex-col gap-2 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between">
        <p>Chelsea Stats · unofficial fan comparison. Not affiliated with Chelsea Football Club.</p>
        {demo ? <p>Demo data until live API keys are connected.</p> : <p>Live results via football-data.org and API-Football.</p>}
      </div>
    </footer>
  );
}
