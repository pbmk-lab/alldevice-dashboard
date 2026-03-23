# Phase 4: Device drilldown and work reports - Context

**Gathered:** 2026-03-23
**Status:** In progress

<domain>
## Phase Boundary

Phase 4 deepens the operator-facing frontend for device drilldown and work reports.
The goal is to connect asset-level downtime burden with technician and service effort,
using the existing backend contracts as the source of truth.

</domain>

<decisions>
## Implementation Decisions

### Product surface
- **D-01:** Devices should support a line-focused view so managers can inspect the worst device burden within a selected operational slice.
- **D-02:** Work reports should emphasize labor allocation and effort concentration before raw tabular detail.
- **D-03:** The UI should stay consistent with the operator workspace direction established in Overview and Triage.

### the agent's Discretion
- Devices may use a query-string-backed line selector if it keeps drilldown shareable and simple.
- Raw report rows can stay secondary until a later admin/reporting slice.

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
- `frontend/src/features/devices/DevicesPage.tsx`
- `frontend/src/features/work-reports/WorkReportsPage.tsx`
- `frontend/src/shared/ui/layout.tsx`
- `frontend/src/shared/api/client.ts`
- `frontend/src/shared/i18n/translations.ts`
- `frontend/src/index.css`

### Backend contract
- `backend/app/domain/models.py`
- `backend/app/api/routes/devices.py`
- `backend/app/api/routes/work_reports.py`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `ChartPanel` already supports bar and trend views without additional chart plumbing.
- The shell already passes `availableLines` and shared filters through the outlet context.

### Established Patterns
- Query state lives in the URL via `useSearchParams`.
- Presentation emphasis may be derived client-side as long as backend values remain the source data.

### Integration Points
- `api.devices(filters, line)` already supports line drilldown.
- Work report KPIs and aggregates are already typed and available from `/api/work-reports`.

</code_context>

<specifics>
## Specific Ideas

- Devices should expose a “focus asset” block with a line selector and top-cause context.
- Work reports should expose a technician/service/line allocation board plus a compact raw table.

</specifics>

<deferred>
## Deferred Ideas

Full report exports and deeper admin-style tabular workflows remain later-phase work.

</deferred>

---

*Phase: 04-device-drilldown-and-work-reports*
*Context gathered: 2026-03-23*
