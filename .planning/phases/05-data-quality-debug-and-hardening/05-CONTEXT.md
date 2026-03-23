# Phase 5: Data quality, debug, and hardening - Context

**Gathered:** 2026-03-23
**Status:** In progress

<domain>
## Phase Boundary

Phase 5 turns data quality and upstream diagnostics into first-class operational screens.
This phase should make quality debt and upstream health obvious to managers and operators,
while also tightening the product surface so the application feels coherent end-to-end.

</domain>

<decisions>
## Implementation Decisions

### Product surface
- **D-01:** Data quality should highlight operational risk, not just percentages.
- **D-02:** Admin/debug should explain system posture and endpoint failures in an immediately scannable way.
- **D-03:** Hardening for this slice means clearer runtime visibility and more consistent UI behavior, not a large backend redesign.

### the agent's Discretion
- Derived severity/posture can be calculated on the frontend from existing backend values if it keeps contracts unchanged.
- Guidance copy may be concise and operational rather than technical.

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
- `frontend/src/features/data-quality/DataQualityPage.tsx`
- `frontend/src/features/admin-debug/AdminDebugPage.tsx`
- `frontend/src/shared/i18n/translations.ts`
- `frontend/src/index.css`

### Backend contract
- `backend/app/domain/models.py`
- `backend/app/api/routes/data_quality.py`
- `backend/app/api/routes/debug.py`
- `backend/app/services/decision_service.py`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- The workspace layout system built for Overview, Triage, Devices, and Work Reports can be reused directly.
- Existing backend endpoints already expose enough signal for quality and admin posture without schema changes.

### Established Patterns
- Presentation-level prioritization is happening on the frontend while backend remains the source of truth.
- Query scope and locale are already shared through the shell context.

### Integration Points
- `DataQualityPage` consumes anomaly and missing-cause aggregates from `/api/data-quality`
- `AdminDebugPage` consumes endpoint statuses from `/api/debug/upstream`

</code_context>

<specifics>
## Specific Ideas

- Make the worst quality line obvious in one glance.
- Turn debug statuses into an operational readiness board with action hints.

</specifics>

<deferred>
## Deferred Ideas

Deep export tooling, auth/permissions, and broader platform observability remain later work.

</deferred>

---

*Phase: 05-data-quality-debug-and-hardening*
*Context gathered: 2026-03-23*
