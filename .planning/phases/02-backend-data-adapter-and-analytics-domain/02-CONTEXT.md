# Phase 2: Backend data adapter and analytics domain - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 2 hardens the extracted backend domain: upstream payload validation,
analytics normalization, and typed endpoint behavior. The phase should make the
backend a trustworthy source of truth for the frontend, independent from the legacy
Streamlit UI.

</domain>

<decisions>
## Implementation Decisions

### Contract handling
- **D-01:** Preserve the current upstream request payload shape, but validate upstream response shape explicitly before analytics code consumes it.
- **D-02:** Treat malformed or failed upstream responses as backend errors, not as silent empty datasets.
- **D-03:** Expand backend verification around service behavior and API routes before adding more frontend complexity.

### the agent's Discretion
- Validation helpers may live inside `decision_service.py` if they keep route handlers thin.
- Tests can use in-process FastAPI `TestClient` and stubs instead of real upstream calls.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Planning
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`

### Backend source of truth
- `backend/app/clients/alldevice.py`
- `backend/app/services/decision_service.py`
- `backend/app/services/downtime_service.py`
- `backend/app/services/task_reports_service.py`
- `backend/app/api/routes/__init__.py`
- `backend/app/main.py`

### Existing verification
- `tests/backend/test_line_mapping_and_metrics.py`

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `DecisionService` already centralizes endpoint orchestration.
- `downtime_service.py` and `task_reports_service.py` already separate normalization from route code.

### Established Patterns
- Routes are intentionally thin and depend on the shared `DecisionService`.
- Tests already use synthetic rows for deterministic analytics checks.

### Integration Points
- Any validation change in `DecisionService` affects all `/api/*` routes.
- FastAPI exception handlers in `backend/app/main.py` are the place where service errors become stable HTTP responses.

</code_context>

<specifics>
## Specific Ideas

- Add explicit validation for `success` and `response` shape from the downtime endpoint.
- Add API-level tests with dependency overrides to prove route contracts without real upstream calls.

</specifics>

<deferred>
## Deferred Ideas

None.

</deferred>

---

*Phase: 02-backend-data-adapter-and-analytics-domain*
*Context gathered: 2026-03-23*
