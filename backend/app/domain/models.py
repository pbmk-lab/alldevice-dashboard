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


class TechnicianWorkRow(BaseModel):
    technician_name: str
    report_nr: str
    service_name: str
    device_name: str
    line: str
    report_date: str | None = None
    allocated_hours: float
    source_total_hours: float


class TechniciansResponse(BaseModel):
    locale: Locale
    kpis: list[KpiMetric]
    selected_technician: str | None = None
    technician_hours: list[NamedMetric]
    technician_reports: list[NamedMetric]
    service_breakdown: list[NamedMetric]
    device_breakdown: list[NamedMetric]
    line_breakdown: list[NamedMetric]
    rows: list[TechnicianWorkRow]


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


class SparkMetric(BaseModel):
    id: str
    label: str
    value: float
    suffix: str = ""
    trend: list[float] = Field(default_factory=list)


class DonutSlice(BaseModel):
    name: str
    value: float
    color: str


class ProblemDeviceRow(BaseModel):
    device_name: str
    incidents: int
    last_issue: str | None = None
    mtbf_hours: float
    mttr_hours: float


class OpenDowntimeRow(BaseModel):
    device_name: str
    line: str
    started_at: str | None = None
    last_service: str | None = None
    duration_hours: float


class PlannedActualPoint(BaseModel):
    period: str
    planned: float
    actual: float


class MixPoint(BaseModel):
    period: str
    planned: float
    unplanned: float
    quality: float


class OperationsWindowResponse(BaseModel):
    locale: Locale
    spark_metrics: list[SparkMetric]
    task_status: list[DonutSlice]
    problem_devices: list[ProblemDeviceRow]
    open_downtimes: list[OpenDowntimeRow]
    planned_vs_actual: list[PlannedActualPoint]
    mix_trend: list[MixPoint]
    work_hours_12m: list[TrendPoint]


class TaskBoardRow(BaseModel):
    task_id: int
    task_number: str
    device_name: str
    service_name: str
    line: str
    priority: str
    overdue_pct: int
    due_date: str | None = None
    task_status: str | None = None
    status_bucket: str | None = None
    service_type: str | None = None
    assigned_users: list[str] = Field(default_factory=list)
    estimated_hours: float = 0
    spares_cost: float = 0


class TaskMixPoint(BaseModel):
    period: str
    emergency: float
    planned: float
    regular: float


class TaskBoardResponse(BaseModel):
    locale: Locale
    kpis: list[KpiMetric]
    status_buckets: list[NamedMetric]
    priority_breakdown: list[NamedMetric]
    service_type_breakdown: list[NamedMetric]
    overdue_trend: list[TrendPoint]
    distribution_trend: list[TaskMixPoint]
    rows: list[TaskBoardRow]


class CostBreakdownPoint(BaseModel):
    period: str
    labor: float
    extra: float
    spares: float


class CostsResponse(BaseModel):
    locale: Locale
    kpis: list[KpiMetric]
    monthly_total_costs: list[TrendPoint]
    monthly_cost_breakdown: list[CostBreakdownPoint]
    service_costs: list[NamedMetric]
    line_costs: list[NamedMetric]
