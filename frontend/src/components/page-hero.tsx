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
    <section className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-br from-[#034694] via-[#0b2d5c] to-[#061428] p-5 text-white shadow-gold sm:rounded-3xl sm:p-8 lg:p-10">
      <div
        aria-hidden
        className="pointer-events-none absolute -right-8 -top-12 h-36 w-36 rounded-full border-[14px] border-chelsea-gold/20 sm:-right-10 sm:-top-16 sm:h-52 sm:w-52 sm:border-[18px]"
      />
      <p className="text-[10px] font-semibold uppercase tracking-[0.22em] text-chelsea-gold sm:text-xs">{kicker}</p>
      <h1 className="mt-1.5 font-display text-[2rem] leading-[1.1] sm:text-5xl lg:text-6xl">{title}</h1>
      <div className="mt-2 max-w-2xl text-sm leading-relaxed text-white/75 sm:mt-3 sm:text-base">{children}</div>
    </section>
  );
}
