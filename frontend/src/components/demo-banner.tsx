import { useDemoMode } from "./demo-mode";

export function DemoBanner() {
  const { demo, message } = useDemoMode();
  if (!demo) {
    return null;
  }

  return (
    <div className="border-b border-chelsea-gold/25 bg-chelsea-gold/10">
      <div className="page-wrap flex flex-col gap-0.5 py-2 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-chelsea-gold">Demo · sample dataset</p>
        <p className="text-xs text-muted-foreground sm:text-right">{message}</p>
      </div>
    </div>
  );
}
