# Architecture

**Analysis Date:** 2026-03-23

## Pattern Overview

**Overall:** Single-file Streamlit dashboard with linear top-to-bottom execution

**Key Characteristics:**
- All UI, data access, transformation, analytics, and rendering live in `app.py`
- Runtime behavior is controlled by Streamlit reruns plus sidebar state in `app.py`
- There is no module boundary between API layer, business logic, and presentation

## Layers

**Presentation layer:**
- Purpose: Render theme, cards, tables, charts, and page branches
- Location: `app.py`
- Contains: inline CSS, titles, KPI cards, page sections, `st.plotly_chart`, `st.dataframe`
- Depends on: all derived pandas DataFrames and Plotly figures
- Used by: Streamlit runtime

**Configuration layer:**
- Purpose: Read endpoints and credentials
- Location: `app.py`
- Contains: `st.secrets[...]`, fallback empty-string defaults, API payload creation
- Depends on: Streamlit secret store
- Used by: API fetch functions

**Data access layer:**
- Purpose: Fetch downtime data and task reports
- Location: `app.py`
- Contains: `load_data()` and `load_taskreports()` with `@st.cache_data`
- Depends on: `requests.post`, payload dictionaries, external APIs
- Used by: normalization and page branches

**Analytics layer:**
- Purpose: Normalize records, classify downtime, compute KPIs and grouped tables
- Location: `app.py`
- Contains: timestamp parsing, line mapping, anomaly filtering, MTTR/MTBF, aggregations
- Depends on: pandas DataFrames built from API responses
- Used by: figure creation and page rendering

## Data Flow

**Main downtime flow:**

1. `app.py` reads secrets and builds request payloads
2. `load_data()` posts to `BASE_URL` and returns JSON
3. `app.py` converts `response` rows into a pandas DataFrame
4. `app.py` derives `duration_hours`, `month`, `line`, `type`, anomaly flags, KPI inputs, and grouped summaries
5. `app.py` builds Plotly figures from grouped DataFrames
6. `st.sidebar.radio` chooses which page branch renders the final output

**Task reports flow:**

1. User selects `🧾 Task reports` in `app.py`
2. `load_taskreports()` posts to `TASKREPORTS_URL`
3. `app.py` normalizes task report fields into `tr_df`
4. `app.py` computes technician, service, and line hour summaries
5. `app.py` renders charts and a raw data table

**State Management:**
- State is implicit in Streamlit widgets and rerun semantics in `app.py`
- Intermediate state is stored in mutable DataFrames (`df`, `df_filtered`, `df_analysis`, `tr_df`) in `app.py`

## Key Abstractions

**Shared chart styling:**
- Purpose: Apply a consistent dark Plotly theme
- Examples: `apply_common_layout()` in `app.py`
- Pattern: one helper reused across all figures

**Line classification:**
- Purpose: Map free-text device locations into production lines
- Examples: `LINE_MAPPING` and `extract_line()` in `app.py`
- Pattern: substring keyword matching against uppercased location text

**Page routing:**
- Purpose: Switch between dashboard modes
- Examples: `page = st.sidebar.radio(...)` and the `if page == ...` branches in `app.py`
- Pattern: one radio control drives four large render branches

## Entry Points

**Streamlit app entrypoint:**
- Location: `app.py`
- Triggers: `streamlit run app.py`
- Responsibilities: entire application lifecycle from config to rendering

**Dependency manifest:**
- Location: `requirements.txt`
- Triggers: environment bootstrap
- Responsibilities: declare the four Python packages the app imports

## Error Handling

**Strategy:** Fail fast in the main execution path

**Patterns:**
- `try/except` around API loading in `app.py` with `st.error(...)` and `st.stop()`
- Empty/invalid dataset checks in `app.py` that short-circuit rendering

## Cross-Cutting Concerns

**Logging:** Not detected beyond Streamlit-visible errors in `app.py`
**Validation:** Minimal defensive coercion with `pd.to_datetime`, `pd.to_numeric`, and empty-result guards in `app.py`
**Authentication:** API credentials are provided through `st.secrets` in `app.py`

---

*Architecture analysis: 2026-03-23*
