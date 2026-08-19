# Deployment

## One project on Vercel (recommended)

The repo root [`vercel.json`](../vercel.json) uses [Vercel Services](https://vercel.com/docs/services): Vite (`frontend/`) plus FastAPI (`backend/`) on one domain.

**Production URL:** [https://chelsea-pocket.vercel.app](https://chelsea-pocket.vercel.app) (project name `chelsea-pocket`). The previous default host `workspace-mu-one-49.vercel.app` 308-redirects there.

- `/v1/*`, `/health`, `/docs`, `/openapi.json` → FastAPI
- everything else → the SPA

Same-origin fetches mean you do **not** set `VITE_API_BASE_URL` on Vercel.

**Demo flag:** `USE_DEMO_DATA=true` (default) serves sample data for every screen and never calls football-data.org or API-Football. Set it to `false` only after adding live keys.

```bash
npx vercel --prod --yes
```

Or Import the GitHub repo in the Vercel dashboard (root directory = repository root, not `frontend/`).

Optional env on the Vercel project: `FOOTBALL_DATA_API_KEY`, `API_FOOTBALL_KEY`, `DATABASE_URL` (Neon), Upstash Redis, `CORS_ORIGINS` (include the `*.vercel.app` URL if the API is ever called cross-origin), `USE_DEMO_DATA`.

Do not put sports API keys in the Vite env (`VITE_*`).

## Frontend-only Vercel + separate FastAPI

If you split hosts:

1. Vercel project **Root Directory** `frontend`.
2. `VITE_API_BASE_URL` = public FastAPI URL (no trailing slash).
3. Host FastAPI on Render/Railway/Fly (`backend/Dockerfile` or `Procfile`).

## Neon (Lakebase Postgres)

1. Create a project on [Neon](https://neon.tech).
2. Copy the pooled connection string into `DATABASE_URL` (`postgresql+asyncpg://user:pass@host/db?ssl=require`).
3. On first boot the app runs `create_all`. For production migrations:

```bash
cd backend && alembic upgrade head
```

## Upstash Redis

REST (`UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`) on Vercel. Locally: `docker compose up -d redis` and `REDIS_URL=redis://localhost:6379/0`.

## Health

`GET /health` → `{ "status": "ok" }`.
