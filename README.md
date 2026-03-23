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

For container/server deployment, prefer these environment variable aliases:

- `ALLDEVICE_BASE_URL`
- `ALLDEVICE_TASKREPORTS_URL`
- `ALLDEVICE_USERNAME`
- `ALLDEVICE_PASSWORD`
- `ALLDEVICE_API_KEY`

Optional non-secret runtime settings:

- `DEFAULT_DATE_START`
- `DEFAULT_DATE_END`
- `TASKREPORTS_DATE_TYPE`
- `DEFAULT_LOCALE`

## Docker deployment

Build and run with Docker Compose:

```powershell
copy .env.example .env
docker compose up --build
```

The app will be available at:

- `http://127.0.0.1:8000`

Example `.env` values for Compose:

```env
ALLDEVICE_BASE_URL=https://example/api/downtime
ALLDEVICE_TASKREPORTS_URL=https://example/api/taskreports
ALLDEVICE_USERNAME=your-user
ALLDEVICE_PASSWORD=your-password
ALLDEVICE_API_KEY=your-api-key
DEFAULT_DATE_START=2023-01-01
DEFAULT_DATE_END=2026-12-31
TASKREPORTS_DATE_TYPE=completed_date
DEFAULT_LOCALE=lv
```

This container builds the React frontend, bundles it into `frontend/dist`, and serves everything through FastAPI from a single process.

## Coolify deployment

This repo is now set up to deploy in Coolify directly from the `Dockerfile`.

Recommended Coolify setup:

- Build Pack: `Dockerfile`
- Port: `8000`
- Health check path: `/health`
- Domain / proxy: handled by Coolify

Set these environment variables in Coolify:

- `ALLDEVICE_BASE_URL`
- `ALLDEVICE_TASKREPORTS_URL`
- `ALLDEVICE_USERNAME`
- `ALLDEVICE_PASSWORD`
- `ALLDEVICE_API_KEY`

Optional:

- `DEFAULT_DATE_START`
- `DEFAULT_DATE_END`
- `TASKREPORTS_DATE_TYPE`
- `DEFAULT_LOCALE`
- `PORT=8000`

Notes:

- the container already exposes and serves the full app on a single FastAPI process
- the frontend is built during image build, so Coolify only needs to build and run the container
- `.streamlit/secrets.toml` is not needed in Coolify; use environment variables there instead
