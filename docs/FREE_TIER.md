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
| football-data.org v4 | ~10 requests/minute; 12 competitions; no lineups/goals on base free | `GET /v4/teams/{id}/matches`, `GET /v4/competitions/PL/standings` | **Primary** Just Finished scores for the current season; date window required for FINISHED |
| API-Football v3 | 100 requests/day; 10/min; **seasons 2022–2024 only** on free | `GET /fixtures`, `GET /fixtures/players`, `GET /fixtures/events`, `GET /players` | Ratings, events, and compare stats **only** when the match/season is in 2022–2024. Last-resort fixtures if football-data.org and openfootball return nothing |
| StatsBomb Open Data | GitHub raw JSON; be polite | `GET .../data/events/{id}.json` | Optional events when match id is `sb-*` |
| openfootball | GitHub JSON | `GET football.json/{season}/en.1.json` | Fallback current-season scores if football-data.org is empty |

Set `USE_DEMO_DATA=true` for UI work with zero third-party calls.

### Player ratings on free tier

Just Finished always prefers **current-season scores** from football-data.org (then openfootball). API-Football is an enrichment layer: `/fixtures/players` and `/fixtures/events` run only when `season_accessible_on_free_tier` is true (kickoff in 2022–2024). Current-season cards still show the score; ratings/events stay empty with an honest coverage note.

Do **not** replace a current-season result list with older rated API-Football fixtures just to fill the ratings column.

Compare season totals return nothing (not a silent 2024 substitute) when the requested range has no free-tier seasons.

## Platform quotas

| Service | Watch |
|---|---|
| Vercel Hobby | Bandwidth and build minutes; static SPA is cheap |
| Neon free | Compute time and storage; JSONB snapshots stay modest if you only keep Chelsea |
| Upstash Redis free | Command count and max size; cache keys are small JSON |
| Render/Railway free | Cold starts; `/health` for uptime pings |

## Caching policy

- `chelsea:just-finished:v7` — 6 hours; stores up to 10 matches, responses are sliced by `limit`
- `fixture:{match.id}:player_stats:v7` — 7 days (full stat payload)
- `chelsea:context` — 1 hour
- `players:search:{q}` — 1 hour
- Never cache HTTP 429/5xx as a successful empty payload

## Persistence

Snapshots and player rows use **SQLModel** (FastAPI creator ORM) via async SQLAlchemy sessions on Neon. `/health` reports `persistence: true` only when that repository initialized successfully.
