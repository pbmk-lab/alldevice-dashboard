# Roadmap: Alldevice Dashboard Rebuild

## Overview

Rebuild Alldevice from a single-file Streamlit analytics dashboard into a bilingual
internal decision-support web app with a FastAPI backend, a React frontend, preserved
legacy fallback, and GSD-managed phase execution.

## Phases

**Phase Numbering:**
- Integer phases are planned roadmap work
- Each phase can contain one or more plans executed through GSD artifacts

- [x] **Phase 1: Foundation and extraction** - establish the runnable split app foundation
- [x] **Phase 2: Backend data adapter and analytics domain** - validate and harden backend analytics orchestration
- [x] **Phase 3: Overview and line triage product surface** - turn overview and triage into operator workspaces
- [x] **Phase 4: Device drilldown and work reports** - deepen device and labor-effort product surfaces
- [x] **Phase 5: Data quality, debug, and hardening** - elevate quality and debug into operational screens
- [x] **Phase 6: Final hardening and workflow cleanup** - normalize roadmap automation, trim bundle cost, and extend smoke coverage

## Phase Details

### Phase 1: Foundation and extraction
**Goal**: Establish backend/frontend scaffolding, preserve the legacy fallback, centralize configuration, and verify local startup.
**Depends on**: Nothing (first phase)
**Requirements**: [REQ-01, REQ-02, REQ-04, REQ-08]
**Success Criteria** (what must be TRUE):
  1. Backend and frontend both run from the current repo layout
  2. Legacy Streamlit fallback remains callable from `app.py`
  3. Local Python execution path is documented and verified
**Plans**: 1 plan

Plans:
- [x] 01-01: Stabilize runnable foundation

### Phase 2: Backend data adapter and analytics domain
**Goal**: Make backend orchestration and analytics normalization reliable enough to be the source of truth for the frontend.
**Depends on**: Phase 1
**Requirements**: [REQ-01, REQ-03, REQ-05, REQ-06]
**Success Criteria** (what must be TRUE):
  1. Malformed upstream responses fail predictably
  2. Backend route contracts are verified beyond pure helper math
  3. Analytics logic remains typed and separate from UI code
**Plans**: 1 plan

Plans:
- [x] 02-01: Harden backend contract validation

### Phase 3: Overview and line triage product surface
**Goal**: Make overview and triage read like manager-facing operating workspaces instead of generic dashboards.
**Depends on**: Phase 2
**Requirements**: [REQ-03, REQ-04, REQ-07]
**Success Criteria** (what must be TRUE):
  1. Overview surfaces posture, queue, and evidence clearly
  2. Triage ranks lines as an actionable risk ladder
  3. The first viewport explains scope and operating window immediately
**Plans**: 1 plan

Plans:
- [x] 03-01: Upgrade overview and triage into operator workspace

### Phase 4: Device drilldown and work reports
**Goal**: Connect device burden and labor effort through stronger device and work-report product surfaces.
**Depends on**: Phase 3
**Requirements**: [REQ-03, REQ-04, REQ-07]
**Success Criteria** (what must be TRUE):
  1. Devices supports a focused drilldown path by line
  2. Work Reports emphasizes labor allocation before raw detail
  3. Both screens align visually with the operator workspace direction
**Plans**: 1 plan

Plans:
- [x] 04-01: Upgrade devices and work reports into operator workspaces

### Phase 5: Data quality, debug, and hardening
**Goal**: Make data quality debt and upstream diagnostics first-class operational surfaces.
**Depends on**: Phase 4
**Requirements**: [REQ-03, REQ-04, REQ-07]
**Success Criteria** (what must be TRUE):
  1. Data Quality highlights the worst operational quality debt in one glance
  2. Admin / Debug communicates system posture and endpoint health clearly
  3. Quality and admin screens feel consistent with the rest of the product
**Plans**: 1 plan

Plans:
- [x] 05-01: Upgrade quality and admin screens into operational control surfaces

### Phase 6: Final hardening and workflow cleanup
**Goal**: Reduce avoidable frontend bundle cost, normalize roadmap parsing for GSD automation, and broaden smoke coverage.
**Depends on**: Phase 5
**Requirements**: [REQ-06, REQ-08, REQ-09]
**Success Criteria** (what must be TRUE):
  1. GSD tools can detect phases from ROADMAP.md
  2. Chart bundle cost is reduced from the current full Plotly payload
  3. Smoke coverage extends beyond current backend helper and route tests
**Plans**: 1 plan

Plans:
- [x] 06-01: Final hardening and workflow cleanup

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation and extraction | 1/1 | Complete | 2026-03-23 |
| 2. Backend data adapter and analytics domain | 1/1 | Complete | 2026-03-23 |
| 3. Overview and line triage product surface | 1/1 | Complete | 2026-03-23 |
| 4. Device drilldown and work reports | 1/1 | Complete | 2026-03-23 |
| 5. Data quality, debug, and hardening | 1/1 | Complete | 2026-03-23 |
| 6. Final hardening and workflow cleanup | 1/1 | Complete | 2026-03-23 |
