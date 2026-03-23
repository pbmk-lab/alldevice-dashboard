from __future__ import annotations

import asyncio
from datetime import date

from fastapi.testclient import TestClient

from backend.app.api.deps import get_decision_service
from backend.app.clients.alldevice import UpstreamAPIError
from backend.app.core.config import Settings
from backend.app.main import app
from backend.app.services.decision_service import DecisionService


SAMPLE_DOWNTIME_RESPONSE = {
    "success": True,
    "response": [
        {
            "id": 1,
            "start_date": "2025-01-01T08:00:00",
            "end_date": "2025-01-01T10:00:00",
            "duration_seconds": 7200,
            "cat_name": "STOP devējs",
            "device_name": "Press A",
            "device_location": "1 LĪNIJA ZONA",
            "comments": "",
            "is_ended": True,
        }
    ],
}


def build_settings() -> Settings:
    return Settings(
        base_url="https://example.com/base",
        taskreports_url="https://example.com/reports",
        username="u",
        password="p",
        api_key="k",
    )


class StubClient:
    async def fetch_downtime(self, date_start: str, date_end: str) -> dict:
        return SAMPLE_DOWNTIME_RESPONSE

    async def fetch_task_reports(self, date_start: str, date_end: str) -> dict:
        return {
            "success": True,
            "response": {
                "total": 1,
                "data": [
                    {
                        "report_id": 10,
                        "report_nr": "R-10",
                        "service_name": "Inspection",
                        "device_name": "Press A",
                        "device_location": "1 LĪNIJA ZONA",
                        "user_name_list": "Tech A",
                        "total_time_seconds": 3600,
                        "completed_date": "2025-01-01T11:00:00",
                    }
                ],
            }
        }


def test_decision_service_rejects_failed_downtime_response() -> None:
    service = DecisionService(build_settings())

    class FailingStubClient:
        async def fetch_downtime(self, date_start: str, date_end: str) -> dict:
            return {"success": False, "response": []}

        async def fetch_task_reports(self, date_start: str, date_end: str) -> dict:
            return {"response": {"total": 0, "data": []}}

    service.client = FailingStubClient()

    try:
        asyncio.run(service.get_overview("lv", date(2025, 1, 1), date(2025, 1, 31), None))
    except UpstreamAPIError as exc:
        assert "success=false" in str(exc)
    else:
        raise AssertionError("Expected UpstreamAPIError for failed downtime response")


def test_decision_service_builds_work_reports_from_valid_payload() -> None:
    service = DecisionService(build_settings())
    service.client = StubClient()

    payload = asyncio.run(
        service.get_work_reports("lv", date(2025, 1, 1), date(2025, 1, 31), None)
    )

    assert payload.kpis[0].value == 1
    assert payload.technician_hours[0].name == "Tech A"


def test_overview_route_uses_dependency_override() -> None:
    service = DecisionService(build_settings())
    service.client = StubClient()
    app.dependency_overrides[get_decision_service] = lambda: service

    try:
        client = TestClient(app)
        response = client.get(
            "/api/overview",
            params={"date_start": "2025-01-01", "date_end": "2025-01-31", "locale": "lv"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["top_line"] == "01. 1 LĪNIJA"
    assert body["kpis"][0]["id"] == "mttr"


def test_bad_task_report_shape_returns_502() -> None:
    service = DecisionService(build_settings())

    class BadTaskReportClient:
        async def fetch_downtime(self, date_start: str, date_end: str) -> dict:
            return SAMPLE_DOWNTIME_RESPONSE

        async def fetch_task_reports(self, date_start: str, date_end: str) -> dict:
            return {"success": True, "response": []}

    service.client = BadTaskReportClient()
    app.dependency_overrides[get_decision_service] = lambda: service

    try:
        client = TestClient(app)
        response = client.get(
            "/api/work-reports",
            params={"date_start": "2025-01-01", "date_end": "2025-01-31", "locale": "lv"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert "Task reports upstream response must be an object" in response.json()["detail"]


def test_unauthorized_task_reports_returns_502() -> None:
    service = DecisionService(build_settings())

    class UnauthorizedTaskReportClient:
        async def fetch_downtime(self, date_start: str, date_end: str) -> dict:
            return SAMPLE_DOWNTIME_RESPONSE

        async def fetch_task_reports(self, date_start: str, date_end: str) -> dict:
            return {"success": False, "message": "Unauthorized"}

    service.client = UnauthorizedTaskReportClient()
    app.dependency_overrides[get_decision_service] = lambda: service

    try:
        client = TestClient(app)
        response = client.get(
            "/api/work-reports",
            params={"date_start": "2025-01-01", "date_end": "2025-01-31", "locale": "lv"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 502
    assert "Task reports upstream returned success=false" in response.json()["detail"]


def test_debug_route_marks_failed_task_reports_as_not_ok() -> None:
    service = DecisionService(build_settings())

    class UnauthorizedBothClient:
        async def fetch_downtime(self, date_start: str, date_end: str) -> dict:
            return {"success": False, "message": "Unauthorized"}

        async def fetch_task_reports(self, date_start: str, date_end: str) -> dict:
            return {"success": False, "message": "Unauthorized", "response": {}}

    service.client = UnauthorizedBothClient()
    app.dependency_overrides[get_decision_service] = lambda: service

    try:
        client = TestClient(app)
        response = client.get(
            "/api/debug/upstream",
            params={"date_start": "2025-01-01", "date_end": "2025-01-31"},
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    statuses = {item["endpoint"]: item for item in response.json()["statuses"]}
    assert statuses["downtime"]["ok"] is False
    assert statuses["downtime"]["details"] == "success=false"
    assert statuses["task_reports"]["ok"] is False
    assert statuses["task_reports"]["details"] == "success=false"
