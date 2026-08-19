import { Link, NavLink } from "react-router-dom";
import { Moon, Sun } from "lucide-react";

import { Badge } from "./ui/badge";
import { Button } from "./ui/button";
import { useDemoMode } from "./demo-mode";
import { useTheme } from "./theme-provider";

export function AppHeader() {
  const { theme, toggle } = useTheme();
  const { demo } = useDemoMode();

  return (
    <header className="sticky top-0 z-20 border-b border-border/70 bg-chelsea-navy/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <Link to="/" className="flex items-center gap-3">
          <span className="flex h-10 w-10 items-center justify-center rounded-full bg-chelsea-blue text-lg font-display text-chelsea-gold ring-2 ring-chelsea-gold">
            CFC
          </span>
          <div>
            <p className="font-display text-lg leading-none text-white">Chelsea Stats</p>
            <p className="text-xs text-white/70">Just finished · historical compare</p>
          </div>
          {demo ? <Badge className="hidden sm:inline-flex">Demo</Badge> : null}
        </Link>
        <nav className="flex items-center gap-2">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `rounded-full px-3 py-1.5 text-sm font-medium ${
                isActive ? "bg-chelsea-gold text-chelsea-navy" : "text-white/80 hover:text-white"
              }`
            }
          >
            Just Finished
          </NavLink>
          <NavLink
            to="/compare"
            className={({ isActive }) =>
              `rounded-full px-3 py-1.5 text-sm font-medium ${
                isActive ? "bg-chelsea-gold text-chelsea-navy" : "text-white/80 hover:text-white"
              }`
            }
          >
            Compare
          </NavLink>
          <Button variant="ghost" size="sm" onClick={toggle} aria-label="Toggle theme" className="text-white">
            {theme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </Button>
        </nav>
      </div>
    </header>
  );
}
