import type { ReactNode } from "react";

export function PageHero({
  kicker,
  title,
  children,
}: {
  kicker: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="relative overflow-hidden rounded-3xl border border-white/10 bg-gradient-to-br from-[#034694] via-[#0b2d5c] to-[#061428] p-6 text-white shadow-gold sm:p-8">
      <div
        aria-hidden
        className="pointer-events-none absolute -right-10 -top-16 h-48 w-48 rounded-full border-[18px] border-chelsea-gold/25"
      />
      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-chelsea-gold">{kicker}</p>
      <h1 className="mt-2 font-display text-4xl leading-tight sm:text-5xl">{title}</h1>
      <div className="mt-3 max-w-2xl text-sm leading-relaxed text-white/75 sm:text-base">{children}</div>
    </section>
  );
}
