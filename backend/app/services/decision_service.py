from __future__ import annotations

from datetime import date
from typing import Any

from backend.app.clients.alldevice import AlldeviceClient, UpstreamAPIError
from backend.app.core.config import Settings
from backend.app.domain.models import (
    CostsResponse,
    DataQualityResponse,
    DebugEndpointStatus,
    DebugResponse,
    DevicesResponse,
    FiltersResponse,
    Locale,
    OperationsWindowResponse,
    OverviewResponse,
    TaskBoardResponse,
    TriageResponse,
    WorkReportsResponse,
)
from backend.app.services.operations_window_service import build_operations_window_payload
from backend.app.services.downtime_service import (
    build_bundle,
    build_devices_payload,
    build_filters_payload,
    build_overview_payload,
    build_quality_payload,
    build_triage_payload,
    normalize_downtime_rows,
)
from backend.app.services.task_reports_service import (
    build_work_reports_payload,
    filter_task_reports,
    normalize_task_report_rows,
)
from backend.app.services.task_service import (
    build_costs_payload,
    build_task_board_payload,
    filter_tasks,
    normalize_task_rows,
)


class DecisionService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = AlldeviceClient(settings)

    @staticmethod
    def _extract_downtime_rows(response: dict[str, Any]) -> list[dict[str, Any]]:
        if not response.get("success", False):
            raise UpstreamAPIError("Downtime upstream returned success=false")

        rows = response.get("response", [])
        if not isinstance(rows, list):
            raise UpstreamAPIError("Downtime upstream response must be a list")
        return rows

    @staticmethod
    def _extract_task_reports_payload(
        response: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], int]:
        if not response.get("success", False):
            raise UpstreamAPIError("Task reports upstream returned success=false")

        response_obj = response.get("response", {})
        if not isinstance(response_obj, dict):
            raise UpstreamAPIError("Task reports upstream response must be an object")

        rows = response_obj.get("data", [])
        if not isinstance(rows, list):
            raise UpstreamAPIError("Task reports data must be a list")

        total_reports = response_obj.get("total", 0)
        try:
            total_reports_api = int(total_reports)
        except (TypeError, ValueError) as exc:
            raise UpstreamAPIError("Task reports total must be numeric") from exc

        return rows, total_reports_api

    @staticmethod
    def _extract_tasks_payload(response: dict[str, Any]) -> list[dict[str, Any]]:
        if not response.get("success", False):
            raise UpstreamAPIError("Tasks upstream returned success=false")

        response_obj = response.get("response", {})
        if not isinstance(response_obj, dict):
            raise UpstreamAPIError("Tasks upstream response must be an object")

        rows = response_obj.get("data", [])
        if not isinstance(rows, list):
            raise UpstreamAPIError("Tasks upstream data must be a list")
        return rows

    async def get_filters(self, locale: Locale) -> FiltersResponse:
        response = await self.client.fetch_downtime(
            self.settings.default_date_start,
            self.settings.default_date_end,
        )
        rows = self._extract_downtime_rows(response)
        df = normalize_downtime_rows(rows, locale)
        return build_filters_payload(df, self.settings)

    async def get_overview(
        self,
        locale: Locale,
        date_start: date,
        date_end: date,
        lines: list[str] | None,
    ) -> OverviewResponse:
        response = await self.client.fetch_downtime(str(date_start), str(date_end))
        df = normalize_downtime_rows(self._extract_downtime_rows(response), locale)
        bundle = build_bundle(df, lines, date_start, date_end, self.settings.analysis_max_hours)
        return build_overview_payload(locale, bundle, self.settings)

    async def get_triage(
        self,
        locale: Locale,
        date_start: date,
        date_end: date,
        lines: list[str] | None,
    ) -> TriageResponse:
        response = await self.client.fetch_downtime(str(date_start), str(date_end))
        df = normalize_downtime_rows(self._extract_downtime_rows(response), locale)
        bundle = build_bundle(df, lines, date_start, date_end, self.settings.analysis_max_hours)
        return build_triage_payload(locale, bundle)

    async def get_operations_window(
        self,
        locale: Locale,
        date_start: date,
        date_end: date,
        lines: list[str] | None,
    ) -> OperationsWindowResponse:
        downtime_response = await self.client.fetch_downtime(str(date_start), str(date_end))
        downtime_df = normalize_downtime_rows(self._extract_downtime_rows(downtime_response), locale)
        bundle = build_bundle(downtime_df, lines, date_start, date_end, self.settings.analysis_max_hours)

        task_reports_response = await self.client.fetch_task_reports(str(date_start), str(date_end))
        task_rows, _ = self._extract_task_reports_payload(task_reports_response)
        task_df = normalize_task_report_rows(task_rows)
        filtered_task_reports = filter_task_reports(task_df, lines, date_start, date_end)
        return build_operations_window_payload(locale, bundle, filtered_task_reports, date_start, date_end)

    async def get_devices(
        self,
        locale: Locale,
        date_start: date,
        date_end: date,
        lines: list[str] | None,
        line: str | None,
    ) -> DevicesResponse:
        response = await self.client.fetch_downtime(str(date_start), str(date_end))
        df = normalize_downtime_rows(self._extract_downtime_rows(response), locale)
        bundle = build_bundle(df, lines, date_start, date_end, self.settings.analysis_max_hours)
        return build_devices_payload(locale, bundle, line)

    async def get_work_reports(
        self,
        locale: Locale,
        date_start: date,
        date_end: date,
        lines: list[str] | None,
    ) -> WorkReportsResponse:
        response = await self.client.fetch_task_reports(str(date_start), str(date_end))
        rows, total_reports_api = self._extract_task_reports_payload(response)
        df = normalize_task_report_rows(rows)
        filtered = filter_task_reports(df, lines, date_start, date_end)
        return build_work_reports_payload(locale, filtered, total_reports_api)

    async def get_task_board(
        self,
        locale: Locale,
        date_start: date,
        date_end: date,
        lines: list[str] | None,
    ) -> TaskBoardResponse:
        response = await self.client.fetch_tasks(str(date_start), str(date_end))
        df = normalize_task_rows(self._extract_tasks_payload(response))
        filtered = filter_tasks(df, lines, date_start, date_end)
        return build_task_board_payload(locale, filtered)

    async def get_costs(
        self,
        locale: Locale,
        date_start: date,
        date_end: date,
        lines: list[str] | None,
    ) -> CostsResponse:
        response = await self.client.fetch_task_reports(str(date_start), str(date_end))
        rows, _ = self._extract_task_reports_payload(response)
        df = normalize_task_report_rows(rows)
        filtered = filter_task_reports(df, lines, date_start, date_end)
        return build_costs_payload(locale, filtered)

    async def get_data_quality(
        self,
        locale: Locale,
        date_start: date,
        date_end: date,
        lines: list[str] | None,
    ) -> DataQualityResponse:
        response = await self.client.fetch_downtime(str(date_start), str(date_end))
        df = normalize_downtime_rows(self._extract_downtime_rows(response), locale)
        bundle = build_bundle(df, lines, date_start, date_end, self.settings.analysis_max_hours)
        return build_quality_payload(locale, bundle)

    async def get_debug(
        self,
        date_start: date,
        date_end: date,
    ) -> DebugResponse:
        downtime = await self.client.fetch_downtime(str(date_start), str(date_end))
        task_reports = await self.client.fetch_task_reports(str(date_start), str(date_end))
        downtime_success = bool(downtime.get("success", False))
        task_reports_success = bool(task_reports.get("success", False))
        task_reports_response = task_reports.get("response", {})
        task_reports_response_is_dict = isinstance(task_reports_response, dict)

        statuses = [
            DebugEndpointStatus(
                endpoint="downtime",
                ok=downtime_success,
                row_count=len(downtime.get("response", []))
                if isinstance(downtime.get("response", []), list)
                else 0,
                details=(
                    "success=true"
                    if downtime_success
                    else "success=false" if "success" in downtime else "missing success flag"
                ),
            ),
            DebugEndpointStatus(
                endpoint="task_reports",
                ok=task_reports_success and task_reports_response_is_dict,
                row_count=len(task_reports_response.get("data", []))
                if task_reports_response_is_dict
                else 0,
                details=(
                    "success=true, dict response object"
                    if task_reports_success and task_reports_response_is_dict
                    else "success=false"
                    if not task_reports_success and "success" in task_reports
                    else "unexpected response shape"
                    if not task_reports_response_is_dict
                    else "missing success flag"
                ),
            ),
        ]
        return DebugResponse(statuses=statuses)
