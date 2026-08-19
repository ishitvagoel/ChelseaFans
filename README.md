# ChelseaFans — Historical & Recent Stats Comparison

Production-oriented app for Chelsea supporters: **Just Finished** matches (events + key player stats) and **side-by-side player/season comparison**. Multiple free data sources are normalized into one domain model, with aggressive caching so free tiers survive.

- **Frontend:** Vite + React + TypeScript + Tailwind + shadcn-style UI (Vercel)
- **Backend:** FastAPI BFF (Render / Railway / Fly)
- **Database:** Neon (Lakebase Postgres) behind `ISnapshotRepository`
- **Cache:** Upstash Redis or TCP Redis, with in-memory fallback

## SOLID from conceptualization

Design happened **before** folders. Each major choice maps to a change axis.

| Decision | SOLID justification |
|---|---|
| Split provider ports (`IFixtureProvider`, `IPlayerMatchStatsProvider`, …) instead of `IFootballApi` | **ISP** — football-data.org does not implement ratings; StatsBomb does not implement standings. Callers should not depend on unused methods. |
| `ProviderRegistry` + one class per source | **SRP** + **OCP** — add Understat by implementing ports and registering; do not edit merge math. |
| Domain types with `None` + `DataConfidence`, never invented zeros | **LSP** — a sparse adapter remains a valid substitute. |
| `composition.py` wires Redis, Neon, httpx clients | **DIP** — use cases depend on ports. |
| FastAPI routers only map HTTP | **SRP** — OpenAPI versioning can change without touching football rules. |
| React talks only to the BFF | **SRP** / security — UI is a presentation adapter; sports API keys stay on the server. |
| Comparison engine is pure functions | **SRP** — new chart metrics do not require cache or HTTP changes. |
| Postgres (Neon) + JSONB snapshots, SQL repositories | Relational identity map (`external_ids`) needs uniqueness; **DIP** via `ISnapshotRepository` so MongoDB Atlas could store bulky raw payloads later without rewriting use cases. |
| Demo provider implements the same ports | **OCP** — local/dev is an adapter, not an `if DEMO` forest in services. |

### Why Neon / Postgres (not NoSQL as primary)

Matches, players, and provider IDs are relational. Free Neon (serverless Postgres) fits the stack and unique constraints. Document stores are a valid *adapter* for raw provider blobs; the MVP keeps JSONB in Postgres so there is one brain. To swap: implement `ISnapshotRepository` (see `backend/app/domain/interfaces.py`).

### Why FastAPI + Vite (not Next.js)

The plan requires Vite + React. Fusion of three sports APIs belongs in one application layer with DI, rate limits, and snapshots — a BFF — not in the browser or in duplicated RSC fetchers.

## Architecture

```
React SPA  →  FastAPI /v1  →  application services  →  ports
                                      ↓
                    ProviderRegistry (confidence + fallback)
                                      ↓
         football-data.org | API-Football | StatsBomb | openfootball | demo
                                      ↓
                         ICache  +  ISnapshotRepository
```

Chelsea club IDs are configuration (`CHELSEA_FOOTBALL_DATA_TEAM_ID=61`, `CHELSEA_API_FOOTBALL_TEAM_ID=49`), not scattered literals.

## How to add a data provider

1. Architecture: confirm an existing port fits (ISP). Add a port only if the capability is new.
2. Providers: create `backend/app/infrastructure/providers/your_source.py` mapping JSON → domain.
3. Backend: register the instance in `backend/app/composition.py`.
4. Do not change `JustFinishedService` / `ComparisonService` internals for source-specific branches.
5. Document quota in `docs/FREE_TIER.md`.

## Agents

Specialized personas and hand-offs live in [AGENTS.md](AGENTS.md). The Architecture & Domain Agent always designs first.

## Local development

```bash
# API
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # USE_DEMO_DATA=true works with no keys
uvicorn app.main:app --reload --port 8000

# optional Redis
docker compose up -d redis

# UI
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`. API docs: `http://localhost:8000/docs`.

## Tests

```bash
cd backend && pytest
cd frontend && npm test
```

## Deploy

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) and [docs/FREE_TIER.md](docs/FREE_TIER.md).

Frontend types should stay aligned with FastAPI OpenAPI (`GET /openapi.json` → `frontend/src/lib/api-types.ts`).
