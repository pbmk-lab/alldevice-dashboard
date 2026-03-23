# Phase 3: Overview and line triage product surface - Context

**Gathered:** 2026-03-23
**Status:** In progress

<domain>
## Phase Boundary

Phase 3 turns the existing frontend shell into an operator-facing decision workspace.
The emphasis is on overview and line triage: orientation, priority signals, and ranked
actions for managers. This phase improves presentation quality and information hierarchy
without changing backend analytics truth.

</domain>

<decisions>
## Implementation Decisions

### Product surface
- **D-01:** Keep backend math on the server; frontend may derive presentation order and emphasis only.
- **D-02:** The first viewport should behave like an operator workspace, not a marketing hero and not a KPI card wall.
- **D-03:** Overview and triage should prioritize attention, posture, and ranked action over chart inventory.

### Visual direction
- **D-04:** Use a dark navigation rail with a lighter operating canvas.
- **D-05:** Favor strips, ranked rows, and evidence sections over default dashboard card mosaics.

### the agent's Discretion
- Minor supporting copy and layout refinements can be introduced as long as they preserve bilingual operation and manager-first scanning.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning and state
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`

### Frontend source files
- `frontend/src/shared/ui/layout.tsx`
- `frontend/src/features/overview/OverviewPage.tsx`
- `frontend/src/features/triage/TriagePage.tsx`
- `frontend/src/shared/api/client.ts`
- `frontend/src/shared/i18n/translations.ts`
- `frontend/src/index.css`

### Backend contract
- `backend/app/domain/models.py`
- `backend/app/api/routes/overview.py`
- `backend/app/api/routes/triage.py`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- Shared chart wrapper already exists in `frontend/src/shared/ui/chart-panel.tsx`
- Shared shell and query handling already live in `frontend/src/shared/ui/layout.tsx`

### Established Patterns
- Frontend uses React Router + TanStack Query
- Relative `/api/*` calls are already normalized through the Vite proxy and FastAPI production serving

### Integration Points
- `OverviewPage` and `TriagePage` consume already-typed backend responses
- Any UI deepening should preserve the same API contracts so backend and frontend stay loosely coupled

</code_context>

<specifics>
## Specific Ideas

- Push important operational context into the first visible screen area
- Make triage rankings legible without requiring chart interpretation first

</specifics>

<deferred>
## Deferred Ideas

Deeper device drilldown, work report presentation, and data quality administration remain later phase work.

</deferred>

---

*Phase: 03-overview-and-line-triage-product-surface*
*Context gathered: 2026-03-23*
