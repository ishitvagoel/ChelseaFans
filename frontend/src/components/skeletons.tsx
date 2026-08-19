export function SkeletonBlock({ className }: { className?: string }) {
  return <div className={`skeleton h-24 ${className ?? ""}`} />;
}

export function MatchListSkeleton() {
  return (
    <div className="grid gap-4" aria-hidden>
      <SkeletonBlock className="h-36" />
      <SkeletonBlock className="h-56" />
      <SkeletonBlock className="h-56" />
    </div>
  );
}
