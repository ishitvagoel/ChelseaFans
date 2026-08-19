import { lazy, Suspense } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { AppFooter } from "./components/app-footer";
import { AppHeader } from "./components/app-header";
import { DemoBanner } from "./components/demo-banner";
import { DemoModeProvider } from "./components/demo-mode";
import { MatchListSkeleton } from "./components/skeletons";
import { ThemeProvider } from "./components/theme-provider";
import { JustFinishedPage } from "./features/just-finished/just-finished-page";

const ComparisonPage = lazy(async () => {
  const module = await import("./features/comparison/comparison-page");
  return { default: module.ComparisonPage };
});

export function App() {
  return (
    <ThemeProvider>
      <DemoModeProvider>
        <BrowserRouter>
          <div className="flex min-h-screen flex-col">
            <AppHeader />
            <DemoBanner />
            <main id="main" className="flex-1">
              <Suspense fallback={<div className="page-wrap py-8"><MatchListSkeleton /></div>}>
                <Routes>
                  <Route path="/" element={<JustFinishedPage />} />
                  <Route path="/compare" element={<ComparisonPage />} />
                </Routes>
              </Suspense>
            </main>
            <AppFooter />
          </div>
        </BrowserRouter>
      </DemoModeProvider>
    </ThemeProvider>
  );
}
