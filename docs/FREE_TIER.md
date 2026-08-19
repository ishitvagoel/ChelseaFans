# Free-tier limits

Stay snapshot-first. Finished Chelsea matches do not change; do not re-fetch them every page load.

## Sports APIs

| Source | Typical free constraint | App behavior |
|---|---|---|
| football-data.org v4 | About 10 requests/minute (free) | Min-interval limiter; Redis + Postgres snapshot for `FINISHED` |
| API-Football v3 | About 100 requests/day on the free plan | Used only to enrich player ratings; skip when remaining quota is low |
| StatsBomb Open Data | GitHub raw JSON; be polite | Long TTL cache; optional enrichment |
| openfootball | GitHub JSON | Same as StatsBomb |

Set `USE_DEMO_DATA=true` for UI work with zero third-party calls.

## Platform quotas

| Service | Watch |
|---|---|
| Vercel Hobby | Bandwidth and build minutes; static SPA is cheap |
| Neon free | Compute time and storage; JSONB snapshots stay modest if you only keep Chelsea |
| Upstash Redis free | Command count and max size; cache keys are small JSON |
| Render/Railway free | Cold starts; `/health` for uptime pings |

## Caching policy

- `chelsea:just-finished:{limit}` — 6 hours (safe; finished results)
- `fixture:{provider}:{id}:players` — 7 days
- `chelsea:context` — 1 hour
- `players:search:{q}` — 1 hour
- Never cache HTTP 429/5xx as a successful empty payload
