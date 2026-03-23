# Phase 1: Foundation and extraction - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 1 establishes the runnable application foundation for the rebuild:
backend/frontend scaffolding, preserved legacy fallback, centralized configuration,
and a reproducible local development path. It does not attempt full product parity
or advanced analytics redesign; the immediate target is a stable base that supports
later phases.

</domain>

<decisions>
## Implementation Decisions

### Platform shape
- **D-01:** Keep the rebuild split into `backend/` and `frontend/`, with FastAPI serving built frontend assets in production.
- **D-02:** Preserve the existing upstream API contracts and secret names exactly in Phase 1.
- **D-03:** Keep the legacy Streamlit application runnable through `legacy/streamlit_app.py` and the root `app.py` compatibility shim.

### Delivery priorities
- **D-04:** Prioritize runnable foundation and verification over feature expansion.
- **D-05:** Make Latvian the default locale while keeping English available in the new UI shell.
- **D-06:** Use manager-first navigation and screens now, but accept shallow data presentation where needed until later phases deepen the product.

### the agent's Discretion
- Dev ergonomics around local startup may be improved if they do not change user-facing contracts.
- Frontend performance and chunking can be improved as part of foundation hardening.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project planning
- `.planning/PROJECT.md` — project statement and target audience
- `.planning/REQUIREMENTS.md` — locked constraints and must-haves
- `.planning/ROADMAP.md` — phase boundaries
- `.planning/STATE.md` — current session state

### Legacy source of truth
- `legacy/streamlit_app.py` — analytics behavior and upstream payload contract
- `app.py` — compatibility entrypoint for the legacy fallback

### Current rebuild surface
- `backend/app/core/config.py` — preserved secrets contract
- `backend/app/main.py` — FastAPI entrypoint and static serving
- `frontend/src/app/router.tsx` — current product shell structure
- `frontend/src/shared/api/client.ts` — internal API contract used by the frontend

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `backend/app/services/downtime_service.py` — normalized downtime analytics already extracted from the legacy app
- `backend/app/services/task_reports_service.py` — task report normalization and summaries
- `frontend/src/shared/ui/layout.tsx` — reusable application shell with filters and locale switch
- `frontend/src/shared/ui/chart-panel.tsx` — shared chart wrapper currently used across screens

### Established Patterns
- Backend is organized by `core` / `clients` / `domain` / `services` / `api/routes`.
- Frontend uses React Router and TanStack Query with route-level screens.
- API fetches use relative `/api/*` paths and therefore need local dev proxy support.

### Integration Points
- FastAPI routes under `backend/app/api/routes/` are the source of truth for frontend data.
- `frontend/dist` is intended to be served by FastAPI in production mode.
- `.streamlit/secrets.toml` remains the local secret source when env vars are absent.

</code_context>

<specifics>
## Specific Ideas

- Stabilize local startup first: Python dependencies, backend import path, frontend dev proxy, and build verification.
- Reduce the initial frontend bundle size enough that the manager shell remains practical to iterate on.

</specifics>

<deferred>
## Deferred Ideas

None - the current focus is foundation hardening inside the original phase boundary.

</deferred>

---

*Phase: 01-foundation-and-extraction*
*Context gathered: 2026-03-23*
