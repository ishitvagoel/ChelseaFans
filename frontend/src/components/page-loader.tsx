export function PageLoader({ label }: { label: string }) {
  return (
    <div
      role="status"
      aria-live="polite"
      className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-border/60 bg-card/50 px-4 py-10 text-center"
    >
      <div
        className="h-11 w-11 animate-spin rounded-full border-2 border-chelsea-gold/25 border-t-chelsea-gold"
        aria-hidden
      />
      <p className="text-sm font-semibold text-chelsea-gold">{label}</p>
      <p className="max-w-sm text-xs text-muted-foreground">
        First load talks to live football APIs and can take a few seconds. Later visits use cache.
      </p>
    </div>
  );
}

export function InlineLoader({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-2 text-sm text-muted-foreground" role="status">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-chelsea-gold/30 border-t-chelsea-gold" />
      <span>{label}</span>
    </div>
  );
}
