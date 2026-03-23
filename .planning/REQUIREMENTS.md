# REQUIREMENTS

## Must Have

- `REQ-01` Preserve current upstream secrets and request payload contracts
- `REQ-02` Keep the legacy Streamlit app runnable during migration
- `REQ-03` Expose manager-first API endpoints for overview, triage, devices, work reports, quality, and debug
- `REQ-04` Support Latvian and English UI
- `REQ-05` Provide typed analytics and line mapping outside the UI layer

## Should Have

- `REQ-06` Automated backend tests for line mapping, anomaly filtering, MTTR, MTBF, and quality rules
- `REQ-07` Frontend shell with manager-first information architecture
- `REQ-08` FastAPI serving built frontend assets for internal deployment
- `REQ-09` GSD-compatible planning artifacts that can be parsed without manual reconstruction

## Out of Scope

- authentication/SSO
- persistent database
- upstream API contract redesign
