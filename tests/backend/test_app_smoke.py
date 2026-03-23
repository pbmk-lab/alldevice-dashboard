from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.api.deps import get_decision_service
from backend.app.main import app


class SmokeDecisionService:
    async def get_filters(self, locale: str):
        return {
            "lines": ["01. 1 LĪNIJA"],
            "min_date": "2025-01-01",
            "max_date": "2025-01-31",
            "default_start": "2025-01-01",
            "default_end": "2025-01-31",
            "default_locale": locale,
        }


def test_health_endpoint_returns_ok() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_filters_route_is_reachable_with_dependency_override() -> None:
    app.dependency_overrides[get_decision_service] = lambda: SmokeDecisionService()

    try:
        client = TestClient(app)
        response = client.get("/api/filters", params={"locale": "lv"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["lines"] == ["01. 1 LĪNIJA"]
    assert body["default_locale"] == "lv"
