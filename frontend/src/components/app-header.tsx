import { Link, NavLink } from "react-router-dom";
import { Moon, Sun } from "lucide-react";

import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { useDemoMode } from "./demo-mode";
import { useTheme } from "./theme-provider";
import { cn } from "../lib/utils";

const links = [
  { to: "/", label: "Just Finished" },
  { to: "/compare", label: "Compare" },
] as const;

export function AppHeader() {
  const { theme, toggle } = useTheme();
  const { demo } = useDemoMode();

  return (
    <header className="sticky top-0 z-30 border-b border-white/10 bg-[#061428]/90 pt-[env(safe-area-inset-top)] backdrop-blur-xl">
      <a
        href="#main"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-3 focus:z-50 focus:rounded-full focus:bg-chelsea-gold focus:px-3 focus:py-1 focus:text-chelsea-navy"
      >
        Skip to content
      </a>
      <div className="page-wrap flex items-center justify-between gap-3 py-3">
        <Link to="/" className="flex min-w-0 items-center gap-2.5 sm:gap-3">
          <span
            aria-hidden
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-chelsea-blue text-xs font-display tracking-wide text-chelsea-gold shadow-[0_0_0_2px_#DBA111] sm:h-11 sm:w-11 sm:text-sm"
          >
            CFC
          </span>
          <div className="min-w-0">
            <p className="font-display text-base leading-none text-white sm:text-lg">Chelsea Stats</p>
            <p className="hidden truncate text-xs text-white/60 sm:block">Recent results · historical compare</p>
          </div>
          {demo ? <Badge className="hidden lg:inline-flex">Sample data</Badge> : null}
        </Link>
        <div className="flex items-center gap-1 sm:gap-2">
          <nav className="hidden items-center gap-2 md:flex" aria-label="Primary">
            {links.map((link) => (
              <NavLink
                key={link.to}
                to={link.to}
                className={({ isActive }) =>
                  cn(
                    "rounded-full px-4 py-2 text-sm font-semibold",
                    isActive
                      ? "bg-chelsea-gold text-chelsea-navy"
                      : "text-white/75 hover:bg-white/10 hover:text-white",
                  )
                }
              >
                {link.label}
              </NavLink>
            ))}
          </nav>
          {demo ? <Badge className="lg:hidden">Demo</Badge> : null}
          <Button
            variant="ghost"
            size="sm"
            onClick={toggle}
            aria-label={theme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            className="min-h-11 min-w-11 text-white"
          >
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
        </div>
      </div>
    </header>
  );
}
