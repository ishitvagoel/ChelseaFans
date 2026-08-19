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

Do not put sports API keys in the Vite env (`VITE_*`). They belong only on the FastAPI service.

## Plug in live APIs and Neon

Keep `USE_DEMO_DATA=true` until every required secret is saved. Demo mode never calls football-data.org or API-Football.

### 1. Collect secrets

| Variable | Where to get it | Notes |
|---|---|---|
| `FOOTBALL_DATA_API_KEY` | [football-data.org](https://www.football-data.org/client/register) → account token | Free plan is ~10 req/min. Used for fixtures / results. |
| `API_FOOTBALL_KEY` | [API-Football](https://dashboard.api-football.com/) → API key | Free plan is ~100 req/day. Used for ratings / player stats. Header is `x-apisports-key`. |
| `DATABASE_URL` | [Neon console](https://console.neon.tech) → project → **Connection details** | Use the **pooled** connection. Rewrite the scheme for SQLAlchemy (below). |
| `UPSTASH_REDIS_REST_URL` + `UPSTASH_REDIS_REST_TOKEN` | [Upstash](https://console.upstash.com/) Redis REST | Optional. Without them the API uses in-memory cache (fine for Hobby, resets on cold start). |

Club IDs are already defaults (`CHELSEA_FOOTBALL_DATA_TEAM_ID=61`, `CHELSEA_API_FOOTBALL_TEAM_ID=49`). You do not need to set them unless they change.

**Neon URL rewrite:** copy the pooled string, then change only the scheme:

```text
postgresql://USER:PASS@ep-xxx-pooler.REGION.aws.neon.tech/neondb?sslmode=require
```

to

```text
postgresql+asyncpg://USER:PASS@ep-xxx-pooler.REGION.aws.neon.tech/neondb?ssl=require
```

(`sslmode=require` → `ssl=require` is the form asyncpg expects.)

### 2. Save them on Vercel (project `chelsea-pocket`)

Dashboard: [Environment Variables](https://vercel.com/ishitvagoel-5075s-projects/chelsea-pocket/settings/environment-variables)

Add each name for **Production** and **Preview** (and Development if you use `vercel env pull`):

1. `FOOTBALL_DATA_API_KEY`
2. `API_FOOTBALL_KEY`
3. `DATABASE_URL` (rewritten string)
4. Optional: `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`
5. Last: `USE_DEMO_DATA` = `false`

Mark the keys **Sensitive**. Do **not** set `VITE_API_BASE_URL` (the SPA already calls same-origin `/v1`). Same-origin also means `CORS_ORIGINS` is unused in production unless you host the API on a different origin.

CLI equivalent (paste when prompted, or pipe the value):

```bash
npx vercel env add FOOTBALL_DATA_API_KEY production preview --sensitive
npx vercel env add API_FOOTBALL_KEY production preview --sensitive
npx vercel env add DATABASE_URL production preview --sensitive
npx vercel env add USE_DEMO_DATA production preview
# type: false
```

### 3. Redeploy

Env changes apply only to **new** deployments:

```bash
npx vercel --prod --yes
```

Or **Redeploy** the latest production deployment in the dashboard (uncheck “Use existing Build Cache” if the flag does not flip).

### 4. Confirm live mode

```bash
curl -sS https://chelsea-pocket.vercel.app/health
# expect: {"status":"ok","demo":false}

curl -sS https://chelsea-pocket.vercel.app/v1/meta
# expect: "demo": false
```

Then hard-refresh the site. Just Finished should load real Chelsea results (subject to free-tier rate limits). If `/health` still shows `"demo": true`, the flag was not set on that deployment.

### Local (optional)

Copy `backend/.env.example` → `backend/.env`, fill the same variables, set `USE_DEMO_DATA=false`, and keep `frontend/.env` pointing at `http://localhost:8000`. Never commit `.env`.

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

`GET /health` → `{ "status": "ok", "demo": true|false }`.
