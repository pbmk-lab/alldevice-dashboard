from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import BaseModel, Field


Locale = Literal["lv", "en"]


class FiltersResponse(BaseModel):
    lines: list[str]
    min_date: date
    max_date: date
    default_start: date
    default_end: date
    default_locale: Locale


class KpiMetric(BaseModel):
    id: str
    label: str
    value: float | int
    unit: str | None = None
    status: str | None = None


class AlertItem(BaseModel):
    id: str
    severity: Literal["critical", "warning", "info"]
    title: str
    description: str


class RecommendationItem(BaseModel):
    id: str
    title: str
    description: str


class TrendPoint(BaseModel):
    period: str
    value: float


class NamedMetric(BaseModel):
    name: str
    value: float
    meta: dict[str, Any] = Field(default_factory=dict)


class OverviewResponse(BaseModel):
    locale: Locale
    kpis: list[KpiMetric]
    alerts: list[AlertItem]
    recommendations: list[RecommendationItem]
    top_line: str
    top_device: str
    mttr_trend: list[TrendPoint]
    mtbf_trend: list[TrendPoint]
    downtime_by_line: list[NamedMetric]
    downtime_by_type: list[NamedMetric]
    quality: dict[str, float | int]


class TriageLineRow(BaseModel):
    line: str
    downtime_hours: float
    events: int
    avg_event_hours: float
    missing_pct: float
    anomaly_count: int
    priority: str
    risk_score: float
    top_category: str


class TriageResponse(BaseModel):
    locale: Locale
    rows: list[TriageLineRow]


class DeviceRow(BaseModel):
    device_name: str
    line: str
    downtime_hours: float
    events: int
    avg_event_hours: float


class DevicesResponse(BaseModel):
    locale: Locale
    selected_line: str | None = None
    top_devices: list[DeviceRow]
    category_breakdown: list[NamedMetric]
    monthly_top_device_trend: list[TrendPoint]


class WorkReportsResponse(BaseModel):
    locale: Locale
    kpis: list[KpiMetric]
    technician_hours: list[NamedMetric]
    service_hours: list[NamedMetric]
    line_hours: list[NamedMetric]
    raw_rows: list[dict[str, Any]]


class DataQualityResponse(BaseModel):
    locale: Locale
    missing_category_pct: float
    excluded_anomalies: int
    excluded_anomaly_hours: float
    quality_by_line: list[NamedMetric]
    anomaly_distribution: list[NamedMetric]


class DebugEndpointStatus(BaseModel):
    endpoint: str
    ok: bool
    row_count: int = 0
    details: str


class DebugResponse(BaseModel):
    statuses: list[DebugEndpointStatus]
