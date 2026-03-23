# Alldevice Dashboard

Alldevice is being rebuilt from a single-file Streamlit dashboard into a manager-first internal web application with:

- FastAPI backend for upstream API integration and analytics
- React frontend for the manager-facing UI
- a temporary Streamlit fallback in `legacy/streamlit_app.py`

## Structure

- `backend/` - FastAPI application
- `frontend/` - React/Vite application
- `legacy/` - temporary Streamlit fallback
- `tests/backend/` - backend unit tests
- `.planning/` - GSD project artifacts

## Python setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Backend dev

```powershell
.venv\Scripts\python -m uvicorn backend.app.main:app --reload
```

## Frontend dev

```powershell
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api/*` requests to `http://127.0.0.1:8000`, so the frontend can keep using relative API paths during local development.

## Legacy Streamlit fallback

```powershell
streamlit run app.py
```

## Configuration

The rebuild preserves the legacy secret names:

- `BASE_URL`
- `TASKREPORTS_URL`
- `USERNAME`
- `PASSWORD`
- `API_KEY`

They can be supplied through environment variables or `.streamlit/secrets.toml`.
