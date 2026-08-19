import { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { AppHeader } from "./components/app-header";
import { ThemeProvider } from "./components/theme-provider";
import { JustFinishedPage } from "./features/just-finished/just-finished-page";

const ComparisonPage = lazy(async () => {
  const module = await import("./features/comparison/comparison-page");
  return { default: module.ComparisonPage };
});

export function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <div className="min-h-screen">
          <AppHeader />
          <Suspense fallback={<p className="px-4 py-8 text-muted-foreground">Loading…</p>}>
            <Routes>
              <Route path="/" element={<JustFinishedPage />} />
              <Route path="/compare" element={<ComparisonPage />} />
            </Routes>
          </Suspense>
        </div>
      </BrowserRouter>
    </ThemeProvider>
  );
}
