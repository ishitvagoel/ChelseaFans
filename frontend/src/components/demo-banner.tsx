import { useDemoMode } from "./demo-mode";

export function DemoBanner() {
  const { demo, message } = useDemoMode();
  if (!demo) {
    return null;
  }

  return (
    <div className="border-b border-chelsea-gold/40 bg-chelsea-gold text-chelsea-navy">
      <div className="mx-auto flex max-w-6xl flex-col gap-1 px-4 py-2 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-sm font-semibold tracking-wide">DEMO MODE — sample Chelsea data</p>
        <p className="text-xs sm:text-sm">{message}</p>
      </div>
    </div>
  );
}
