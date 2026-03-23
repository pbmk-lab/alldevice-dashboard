# Technology Stack

**Analysis Date:** 2026-03-23

## Languages

**Primary:**
- Python - entire runtime lives in `app.py`

**Secondary:**
- HTML/CSS inside Python multiline strings in `app.py`

## Runtime

**Environment:**
- Python runtime for Streamlit app execution

**Package Manager:**
- `pip`
- Lockfile: missing

## Frameworks

**Core:**
- Streamlit - UI shell, state, caching, sidebar filters, page rendering in `app.py`
- pandas - API normalization, grouping, KPI computation, filtering in `app.py`
- Plotly Express / Graph Objects - chart rendering in `app.py`
- requests - outbound API POST calls in `app.py`

**Testing:**
- Not detected

**Build/Dev:**
- Streamlit runtime, typically launched with `streamlit run app.py`

## Key Dependencies

**Critical:**
- `streamlit` - app framework declared in `requirements.txt`
- `pandas` - data transformation declared in `requirements.txt`
- `requests` - API client declared in `requirements.txt`
- `plotly` - charting declared in `requirements.txt`

**Infrastructure:**
- No ORM, database client, task runner, or packaging tool detected

## Configuration

**Environment:**
- Runtime configuration comes from `st.secrets` keys `BASE_URL`, `TASKREPORTS_URL`, `USERNAME`, `PASSWORD`, and `API_KEY` in `app.py`
- No committed `.streamlit/secrets.toml` or env template exists in this repository

**Build:**
- No CI/build config detected
- Dependency manifest is `requirements.txt`

## Platform Requirements

**Development:**
- Python environment with packages from `requirements.txt`
- Streamlit secrets configured outside git for `app.py`
- Network reachability to the APIs referenced by `BASE_URL` and `TASKREPORTS_URL`

**Production:**
- Streamlit-hosted or Python-hosted runtime capable of serving `app.py`
- Secret injection for `st.secrets`

---

*Stack analysis: 2026-03-23*
