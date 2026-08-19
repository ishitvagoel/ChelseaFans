import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { fetchMeta } from "../lib/api";
import type { AppMeta } from "../lib/api-types";

type DemoModeValue = AppMeta & { ready: boolean };

const DemoModeContext = createContext<DemoModeValue>({
  demo: false,
  message: "",
  ready: false,
});

export function DemoModeProvider({ children }: { children: ReactNode }) {
  const [meta, setMeta] = useState<DemoModeValue>({
    demo: false,
    message: "",
    ready: false,
  });

  useEffect(() => {
    void fetchMeta()
      .then((next) => setMeta({ ...next, ready: true }))
      .catch(() => {
        setMeta({
          demo: true,
          message: "Sample data is enabled (API meta unavailable).",
          ready: true,
        });
      });
  }, []);

  const value = useMemo(() => meta, [meta]);
  return <DemoModeContext.Provider value={value}>{children}</DemoModeContext.Provider>;
}

export function useDemoMode() {
  return useContext(DemoModeContext);
}
