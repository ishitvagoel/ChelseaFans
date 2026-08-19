import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { fetchMeta } from "../lib/api";
import type { AppMeta } from "../lib/api-types";

const DemoModeContext = createContext<AppMeta>({
  demo: true,
  message: "Sample data",
});

export function DemoModeProvider({ children }: { children: ReactNode }) {
  const [meta, setMeta] = useState<AppMeta>({
    demo: true,
    message: "Sample data is enabled until live API keys are configured.",
  });

  useEffect(() => {
    void fetchMeta()
      .then(setMeta)
      .catch(() => {
        setMeta({
          demo: true,
          message: "Sample data is enabled (API meta unavailable).",
        });
      });
  }, []);

  const value = useMemo(() => meta, [meta]);
  return <DemoModeContext.Provider value={value}>{children}</DemoModeContext.Provider>;
}

export function useDemoMode() {
  return useContext(DemoModeContext);
}
