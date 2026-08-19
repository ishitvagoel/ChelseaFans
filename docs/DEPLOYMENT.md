# Deployment

The UI is a static Vite SPA. The API is a long-running FastAPI process. Do not put football-data.org or API-Football keys on Vercel.

## Frontend — Vercel

1. Import the GitHub repo in Vercel.
2. Set **Root Directory** to `frontend`.
3. Framework preset: Vite. Build: `npm run build`. Output: `dist`.
4. Environment:
   - `VITE_API_BASE_URL` — public URL of FastAPI, no trailing slash (example: `https://chelsea-stats-api.onrender.com`).
5. `frontend/vercel.json` rewrites unknown paths to `index.html` for React Router.

SPA notes: all data fetching is client-side against the BFF. Configure CORS on the API (`CORS_ORIGINS` must include `https://<project>.vercel.app` and production domain).

## Backend — Render (recommended free/cheap)

1. New **Web Service**, repo root.
2. Root directory: `backend`.
3. Build: `pip install -e ".[dev]"` or `pip install -e .`
4. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Env: copy from `backend/.env.example` — `DATABASE_URL` (Neon), Upstash Redis REST or `REDIS_URL`, API keys, `CORS_ORIGINS`.

Railway and Fly.io work the same way (container or Nixpacks + `uvicorn`). FastAPI on Vercel serverless is possible but a poor fit for httpx connection reuse and provider rate-limit state; prefer a small always-on or scale-to-zero instance.

## Neon (Lakebase Postgres)

1. Create a project on [Neon](https://neon.tech).
2. Copy the pooled connection string into `DATABASE_URL` (`postgresql+asyncpg://...`). Replace `postgres://` with `postgresql+asyncpg://`.
3. On first boot the app runs `create_all` for MVP schema. For production, run Alembic:

```bash
cd backend && alembic upgrade head
```

## Upstash Redis

Create a Redis database. Prefer REST (`UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`) on hosts that cannot open TCP 6379. Locally, `docker compose up -d redis` and `REDIS_URL=redis://localhost:6379/0`.

## Health

`GET /health` should return `{ "status": "ok" }` before pointing Vercel at the API.
