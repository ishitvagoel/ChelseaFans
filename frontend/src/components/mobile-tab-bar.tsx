import { NavLink } from "react-router-dom";
import { GitCompare, Trophy } from "lucide-react";

import { cn } from "../lib/utils";

const tabs = [
  { to: "/", label: "Matches", icon: Trophy },
  { to: "/compare", label: "Compare", icon: GitCompare },
] as const;

export function MobileTabBar() {
  return (
    <nav
      aria-label="Mobile"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-white/10 bg-[#061428]/95 pb-[env(safe-area-inset-bottom)] backdrop-blur-xl md:hidden"
    >
      <ul className="grid grid-cols-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <li key={tab.to}>
              <NavLink
                to={tab.to}
                className={({ isActive }) =>
                  cn(
                    "flex min-h-14 flex-col items-center justify-center gap-1 text-[11px] font-semibold",
                    isActive ? "text-chelsea-gold" : "text-white/55",
                  )
                }
              >
                <Icon className="h-5 w-5" aria-hidden />
                {tab.label}
              </NavLink>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
