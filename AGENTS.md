# AGENTS.md — Chelsea FC Stats Comparison

This file defines how specialized AI agents (and human developers) collaborate on this repository. It encodes **SOLID from conceptualization**, Clean Architecture, free-tier discipline, and a Vercel + FastAPI + Neon split.

Read this file **before** writing code. The Architecture & Domain Agent leads every new capability with design, not folders.

---

## Collaboration model (for the main builder)

Work in this order. Do not skip the first step.

1. **Conceptual design (Architecture & Domain Agent)**  
   Identify responsibilities, change axes, interfaces, and extension points. Choose database, cache, API, and hosting abstractions. Write or update domain types and ports. No HTTP clients and no JSX in this step.

2. **Data Providers / API Integration Agent**  
   Implement adapters that satisfy those ports. Register them. Wire caching and rate limits. Do not change domain rules to fit a quirky API — map the API into the domain.

3. **Backend / FastAPI & Data Access Agent**  
   Thin routers, composition root, repositories, migrations. Inject interfaces; never import a concrete provider from a router.

4. **Frontend / React UI-UX Agent**  
   Consume only the BFF (`VITE_API_BASE_URL`). Enforce Chelsea color system and comparison layouts.

5. **Testing, Expandability, Deployment & Documentation Agent**  
   Tests, README accuracy, deploy/free-tier notes, and keep this file aligned with the tree.

### Review order

Architecture interfaces → provider mappings and cache keys → FastAPI contracts/OpenAPI → UI against those contracts → docs/tests.

### Hand-offs

| From | To | Artifact |
|---|---|---|
| Architecture | Providers | New or changed ports in `backend/app/domain/` |
| Providers | Backend | Adapter class + registry registration notes |
| Backend | Frontend | Stable `/v1` JSON + OpenAPI |
| Frontend | Test/Docs | Routes, env vars, UX constraints |
| Any | Architecture | Proposed new abstraction (never a one-off if-else in core services) |

---

## Architecture & Domain Agent

**Single responsibility:** Own the conceptual model. Guardian of SOLID during design: domain boundaries, ports, registry shape, comparison engine purity, database *abstraction*, API surface, deployment *constraints* (not vendor dashboards).

**Owns**

- `backend/app/domain/`
- Comparison engine design (`backend/app/application/comparison_engine.py` — pure functions only)
- High-level application use-case signatures (`JustFinishedService`, `ComparisonService` *interfaces* of behavior)
- Architecture sections of README and the SOLID tables in this file
- Decisions: Neon/Postgres vs document store *behind* `ISnapshotRepository`; FastAPI as BFF; React as presentation adapter

**Must never touch**

- Concrete HTTP to football-data.org / API-Football / GitHub
- Redis/Upstash client internals
- Alembic SQL details beyond “what the repository must persist”
- React components, Tailwind, shadcn
- Provider API keys in frontend env files

**Must enforce**

- SOLID **before** implementation: SRP per concept, ISP (split provider ports), OCP (registry), LSP (optional fields + confidence, never fake zeros), DIP (composition root)
- Internal UUIDs; provider IDs only in an identity map
- Finished-match data treated as immutable once snapshotted
- Frontend never holds third-party sports API keys

**Lead the design phase** by answering, in order:

1. What can change independently (source, cache, DB, UI, metrics)?
2. Which interface does that change hide behind?
3. What is the smallest type that preserves LSP?
4. How does a new provider register without editing orchestrator internals?

---

## Data Providers / API Integration Agent

**Single responsibility:** Talk to the outside world and normalize into domain types. Caching strategy for *provider* responses. Rate limits and free-tier respect for third-party APIs.

**Owns**

- `backend/app/infrastructure/providers/`
- `backend/app/infrastructure/demo/`
- Provider-facing cache key conventions used by the orchestrator
- `backend/app/infrastructure/http/` (shared rate-limited HTTP helper)
- Confidence scoring *per adapter* (honest coverage notes)

**Must never touch**

- Domain dataclass field semantics (propose a domain change via Architecture)
- FastAPI routers
- SQLAlchemy models (persist via snapshot repository port)
- `frontend/`

**Collaborates with**

- Architecture: new ports if a source cannot fit existing ISP splits
- Backend: composition root registration only
- Test/Docs: quota numbers in `docs/FREE_TIER.md`

**Must enforce**

- One class per provider (SRP)
- Map into domain; never leak raw API JSON into API responses
- Prefer cache + snapshot over live calls for `FINISHED` fixtures
- Missing stats are `null`, not `0`, unless the source explicitly reported zero
- Demo provider implements the same ports (OCP)

---

## Backend / FastAPI & Data Access Agent

**Single responsibility:** HTTP adapter, dependency injection, persistence adapters (Neon/Postgres), Redis/Upstash as `ICache`.

**Owns**

- `backend/app/api/`
- `backend/app/composition.py`
- `backend/app/settings.py`
- `backend/app/main.py`
- `backend/app/application/` (orchestration wiring; keep engine pure)
- `backend/app/infrastructure/cache/`
- `backend/app/infrastructure/db/`
- `backend/alembic/` and `backend/alembic.ini`
- `backend/.env.example`

**Must never touch**

- Provider URL/path mapping and JSON parsing (Providers agent)
- React source
- Domain invariants that belong in `domain/` (import and use them)

**Collaborates with**

- Architecture: DTO fields must be projections of domain, not a second model
- Frontend: CORS, versioned `/v1` routes, OpenAPI
- Providers: inject ports, do not construct HTTP clients in routers

**Must enforce**

- DIP: `Depends()` resolves interfaces from the composition root
- Routers stay thin
- `ISnapshotRepository` so Neon can be swapped (SQLite locally, documented Mongo adapter later)
- In-memory cache if Redis is unset (dev must still run)
- `USE_DEMO_DATA` / missing keys must not crash the process

---

## Frontend / React UI-UX Agent

**Single responsibility:** Premium Chelsea-branded presentation of BFF data. Dark mode first. Comparison layouts that work on mobile and desktop.

**Owns**

- `frontend/`
- `frontend/.env.example` (`VITE_API_BASE_URL` only)
- `frontend/vercel.json`

**Must never touch**

- `backend/` except reading OpenAPI/DTO shapes
- Third-party sports API keys
- Domain provider registry

**Collaborates with**

- Backend: types in `frontend/src/lib/api-types.ts` stay aligned with `/openapi.json`
- Test/Docs: screenshots/behavior notes, Vercel SPA rewrites

**Must enforce**

- Colors: primary `#034694`, gold `#DBA111`, red `#ED1C24`, deep navy, clean whites
- Card hierarchy, large readable numbers
- 1–4 player comparison: stack on small screens, grid on large
- Provenance/confidence visible when sources are partial
- `prefers-reduced-motion`
- No business fusion of multiple sports APIs in the browser

---

## Testing, Expandability, Deployment & Documentation Agent

**Single responsibility:** Prove the system, keep it extendable, document free-tier and deploy paths, keep AGENTS.md honest.

**Owns**

- `backend/tests/`
- `frontend` unit tests (Vitest)
- `README.md` (structure and how-to; Architecture owns SOLID *rationale* content)
- `docs/DEPLOYMENT.md`, `docs/FREE_TIER.md`
- Root `docker-compose.yml`, `.gitignore`
- Accuracy of this file vs the real tree

**Must never touch**

- Product UX styling choices
- Provider credentials
- Inventing new domain concepts without Architecture

**Must enforce**

- Tests against ports (demo provider + engine), not live paid APIs
- “How to add a provider” remains a copy-pasteable recipe
- Vercel (frontend) + separate FastAPI host + Neon + Upstash documented
- Quota-safe defaults

---

## SOLID checklist (every change)

- **S:** Would this file need to change for two unrelated reasons? Split it.
- **O:** Can a new provider be added without editing `ProviderOrchestrator` internals? Register only.
- **L:** Can a sparse provider substitute for a rich one without lying about zeros?
- **I:** Are we reintroducing a god `IFootballApi`? Split ports.
- **D:** Do application services import `httpx` or `redis`? They must not.

---

## Tree map (ownership)

```
backend/app/domain/           Architecture
backend/app/application/      Backend (engine purity: Architecture)
backend/app/api/              Backend
backend/app/infrastructure/providers  Data Providers
backend/app/infrastructure/demo       Data Providers
backend/app/infrastructure/cache      Backend
backend/app/infrastructure/db         Backend
frontend/                    Frontend UI-UX
docs/                        Test/Docs (+ Architecture for SOLID sections)
AGENTS.md                    Test/Docs (content rules from Architecture)
```
