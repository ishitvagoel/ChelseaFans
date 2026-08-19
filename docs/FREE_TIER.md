# Free-tier limits

Stay snapshot-first. Finished Chelsea matches do not change; do not re-fetch them every page load.

## Provider contracts

Inbound HTTP JSON is validated with Pydantic models under `backend/app/infrastructure/providers/contracts/` before mapping to domain types.

| Provider | Contract module | Auth |
|---|---|---|
| football-data.org v4 | `contracts/football_data.py` | `X-Auth-Token` |
| API-Football v3 | `contracts/api_football.py` | `x-apisports-key` |
| openfootball JSON | `contracts/openfootball.py` | none (GitHub raw) |
| StatsBomb open data | `contracts/statsbomb.py` | none (GitHub raw) |

## Sports APIs (free tier in this app)

| Source | Typical free constraint | Endpoints used | App behavior |
|---|---|---|---|
| football-data.org v4 | ~10 requests/minute; 12 competitions; no lineups/goals on base free | `GET /v4/teams/{id}/matches`, `GET /v4/competitions/PL/standings` | Primary Just Finished scores; date window required for FINISHED |
| API-Football v3 | 100 requests/day; 10/min; **seasons 2022–2024 only** on free | `GET /fixtures`, `GET /fixtures/players`, `GET /players` | Player ratings + compare; falls back to rated 2024 fixtures when current season cannot enrich |
| StatsBomb Open Data | GitHub raw JSON; be polite | `GET .../data/events/{id}.json` | Optional events when match id is `sb-*` |
| openfootball | GitHub JSON | `GET football.json/{season}/en.1.json` | Fallback fixtures only |

Set `USE_DEMO_DATA=true` for UI work with zero third-party calls.

### Player ratings on free tier

football-data.org supplies current-season scores. API-Football free tier cannot resolve fixtures for 2025/26, so the orchestrator falls back to the latest **rated** Chelsea fixtures from API-Football seasons 2022–2024 when enrichment fails. Upgrade API-Football for current-season `/fixtures/players`.

## Platform quotas

| Service | Watch |
|---|---|
| Vercel Hobby | Bandwidth and build minutes; static SPA is cheap |
| Neon free | Compute time and storage; JSONB snapshots stay modest if you only keep Chelsea |
| Upstash Redis free | Command count and max size; cache keys are small JSON |
| Render/Railway free | Cold starts; `/health` for uptime pings |

## Caching policy

- `chelsea:just-finished:v6` — 6 hours; sliced by `limit`
- `fixture:{match.id}:player_stats:v5` — 7 days (full stat payload)
- `chelsea:context` — 1 hour
- `players:search:{q}` — 1 hour
- Never cache HTTP 429/5xx as a successful empty payload

## Persistence

Snapshots and player rows use **SQLModel** (FastAPI creator ORM) via async SQLAlchemy sessions on Neon.
