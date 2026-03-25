from __future__ import annotations

from datetime import date

import pandas as pd

from backend.app.domain.models import (
    DonutSlice,
    MixPoint,
    OpenDowntimeRow,
    OperationsWindowResponse,
    PlannedActualPoint,
    ProblemDeviceRow,
    SparkMetric,
    TrendPoint,
)
from backend.app.services.downtime_service import DowntimeBundle


def _month_key(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce").dt.to_period("M").astype(str)


def _spark_values(
    frame: pd.DataFrame,
    date_column: str,
    value_column: str,
    agg: str = "sum",
) -> list[float]:
    if frame.empty or date_column not in frame.columns:
        return []

    grouped = frame.assign(period=_month_key(frame[date_column])).groupby("period", as_index=False)[value_column]
    if agg == "mean":
        grouped = grouped.mean()
    else:
        grouped = grouped.sum()
    grouped = grouped.sort_values("period")
    return [round(float(value), 2) for value in grouped[value_column].tolist()]


def _availability_metrics(bundle: DowntimeBundle, selected_line_count: int, start_date: date, end_date: date) -> SparkMetric:
    analysis = bundle.analysis
    if analysis.empty:
        return SparkMetric(id="availability", label="Availability", value=0, suffix="%")

    span_days = max((pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1, 1)
    total_capacity = span_days * 24 * max(selected_line_count, 1)
    total_downtime = float(analysis["duration_hours"].sum())
    overall = max(0.0, 100.0 - (total_downtime / total_capacity * 100.0 if total_capacity else 0.0))

    monthly = (
        analysis.assign(period=analysis["start_date"].dt.to_period("M"))
        .groupby("period", as_index=False)["duration_hours"]
        .sum()
        .sort_values("period")
    )
    trend: list[float] = []
    for _, row in monthly.iterrows():
        period = row["period"]
        if pd.isna(period):
            continue
        capacity = period.days_in_month * 24 * max(selected_line_count, 1)
        value = max(0.0, 100.0 - (float(row["duration_hours"]) / capacity * 100.0 if capacity else 0.0))
        trend.append(round(value, 2))

    return SparkMetric(id="availability", label="Availability", value=round(overall, 2), suffix="%", trend=trend)


def _event_rate_metrics(bundle: DowntimeBundle, start_date: date, end_date: date) -> SparkMetric:
    analysis = bundle.analysis
    if analysis.empty:
        return SparkMetric(id="event_rate", label="Event rate", value=0, trend=[])

    span_days = max((pd.Timestamp(end_date) - pd.Timestamp(start_date)).days + 1, 1)
    overall = round(float(len(analysis)) / span_days, 2)

    grouped = (
        analysis.assign(period=analysis["start_date"].dt.to_period("M"))
        .groupby("period")
        .size()
        .reset_index(name="events")
        .sort_values("period")
    )
    trend: list[float] = []
    for _, row in grouped.iterrows():
        period = row["period"]
        value = float(row["events"]) / max(period.days_in_month, 1)
        trend.append(round(value, 2))

    return SparkMetric(id="event_rate", label="BF", value=overall, trend=trend)


def _mttr_metric(bundle: DowntimeBundle) -> SparkMetric:
    trend = _spark_values(bundle.closed, "start_date", "duration_hours", agg="mean")
    value = round(float(bundle.closed["duration_hours"].mean()), 2) if not bundle.closed.empty else 0.0
    return SparkMetric(id="mttr", label="MTTR", value=value, suffix="h", trend=trend)


def _mtbf_metric(bundle: DowntimeBundle) -> SparkMetric:
    failures = bundle.failures.dropna(subset=["mtbf_hours"]) if not bundle.failures.empty else bundle.failures
    trend = _spark_values(failures, "start_date", "mtbf_hours", agg="mean")
    value = round(float(failures["mtbf_hours"].mean()), 2) if not failures.empty else 0.0
    return SparkMetric(id="mtbf", label="MTBF", value=value, suffix="h", trend=trend)


def _planned_share_metric(bundle: DowntimeBundle) -> SparkMetric:
    analysis = bundle.analysis
    if analysis.empty:
        return SparkMetric(id="planned_share", label="Planned share", value=0, suffix="%")

    planned_mask = analysis["type"].astype(str).str.contains("plān|planned", case=False, regex=True)
    planned_hours = float(analysis.loc[planned_mask, "duration_hours"].sum())
    total_hours = float(analysis["duration_hours"].sum()) or 1.0
    overall = round(planned_hours / total_hours * 100.0, 2)

    monthly = (
        analysis.assign(
            period=analysis["start_date"].dt.to_period("M"),
            is_planned=planned_mask,
        )
        .groupby(["period", "is_planned"], as_index=False)["duration_hours"]
        .sum()
    )
    trend: list[float] = []
    for period, group in monthly.groupby("period"):
        total = float(group["duration_hours"].sum()) or 1.0
        planned = float(group.loc[group["is_planned"], "duration_hours"].sum())
        trend.append(round(planned / total * 100.0, 2))

    return SparkMetric(id="planned_share", label="Planned %", value=overall, suffix="%", trend=trend)


def _quality_metric(bundle: DowntimeBundle) -> SparkMetric:
    analysis = bundle.analysis
    if analysis.empty:
        return SparkMetric(id="quality", label="Cause coverage", value=0, suffix="%")

    known_mask = analysis["cat_name"] != "Nav norādīts"
    overall = round(float(known_mask.mean()) * 100.0, 2)
    grouped = (
        analysis.assign(period=analysis["start_date"].dt.to_period("M"), known=known_mask)
        .groupby("period", as_index=False)["known"]
        .mean()
        .sort_values("period")
    )
    trend = [round(float(value) * 100.0, 2) for value in grouped["known"].tolist()]
    return SparkMetric(id="quality", label="Cause coverage", value=overall, suffix="%", trend=trend)


def _task_status(bundle: DowntimeBundle, end_date: date) -> list[DonutSlice]:
    filtered = bundle.filtered
    if filtered.empty:
        return []

    open_rows = filtered[filtered["is_ended"] != True].copy()
    if open_rows.empty:
        return []

    reference_ts = pd.Timestamp(end_date).replace(hour=23, minute=59, second=59)
    open_rows["age_hours"] = (
        (reference_ts - open_rows["start_date"]).dt.total_seconds() / 3600
    ).clip(lower=0)

    overdue = int((open_rows["age_hours"] > 24).sum())
    today = int((open_rows["start_date"].dt.date == reference_ts.date()).sum())
    in_progress = max(len(open_rows) - overdue - today, 0)

    return [
        DonutSlice(name="Overdue", value=overdue, color="#ff6b77"),
        DonutSlice(name="Today", value=today, color="#7ea6ff"),
        DonutSlice(name="In progress", value=in_progress, color="#c9ccd3"),
    ]


def _problem_devices(bundle: DowntimeBundle) -> list[ProblemDeviceRow]:
    analysis = bundle.analysis
    if analysis.empty:
        return []

    incidents = (
        analysis.groupby("device_name", as_index=False)
        .agg(
            incidents=("duration_hours", "count"),
            last_issue=("start_date", "max"),
        )
        .sort_values(["incidents", "last_issue"], ascending=[False, False])
    )

    closed = bundle.closed
    mttr = (
        closed.groupby("device_name", as_index=False)["duration_hours"]
        .mean()
        .rename(columns={"duration_hours": "mttr_hours"})
        if not closed.empty
        else pd.DataFrame(columns=["device_name", "mttr_hours"])
    )

    device_failures = analysis.sort_values(["device_name", "start_date"]).copy()
    device_failures["prev_start"] = device_failures.groupby("device_name")["start_date"].shift(1)
    device_failures["mtbf_hours"] = (
        (device_failures["start_date"] - device_failures["prev_start"]).dt.total_seconds() / 3600
    )
    mtbf = (
        device_failures.dropna(subset=["mtbf_hours"])
        .groupby("device_name", as_index=False)["mtbf_hours"]
        .mean()
        if not device_failures.empty
        else pd.DataFrame(columns=["device_name", "mtbf_hours"])
    )

    merged = incidents.merge(mtbf, on="device_name", how="left").merge(mttr, on="device_name", how="left").fillna(0)

    return [
        ProblemDeviceRow(
            device_name=str(row["device_name"]),
            incidents=int(row["incidents"]),
            last_issue=pd.to_datetime(row["last_issue"]).strftime("%d.%m.%Y") if pd.notna(row["last_issue"]) else None,
            mtbf_hours=round(float(row["mtbf_hours"]), 2),
            mttr_hours=round(float(row["mttr_hours"]), 2),
        )
        for _, row in merged.head(10).iterrows()
    ]


def _open_downtimes(bundle: DowntimeBundle, task_reports: pd.DataFrame, end_date: date) -> list[OpenDowntimeRow]:
    filtered = bundle.filtered
    if filtered.empty:
        return []

    open_rows = filtered[filtered["is_ended"] != True].copy()
    if open_rows.empty:
        return []

    reference_ts = pd.Timestamp(end_date).replace(hour=23, minute=59, second=59)
    open_rows["duration_live"] = (
        (reference_ts - open_rows["start_date"]).dt.total_seconds() / 3600
    ).clip(lower=0)
    open_rows["open_hours"] = open_rows[["duration_hours", "duration_live"]].max(axis=1)

    last_service = (
        task_reports.dropna(subset=["report_date"])
        .groupby("device_name", as_index=False)["report_date"]
        .max()
        .rename(columns={"report_date": "last_service"})
        if not task_reports.empty and "report_date" in task_reports.columns
        else pd.DataFrame(columns=["device_name", "last_service"])
    )
    merged = open_rows.merge(last_service, on="device_name", how="left").sort_values("open_hours", ascending=False)

    return [
        OpenDowntimeRow(
            device_name=str(row["device_name"]),
            line=str(row["line"]),
            started_at=pd.to_datetime(row["start_date"]).strftime("%d.%m.%Y %H:%M") if pd.notna(row["start_date"]) else None,
            last_service=pd.to_datetime(row["last_service"]).strftime("%d.%m.%Y %H:%M") if pd.notna(row["last_service"]) else None,
            duration_hours=round(float(row["open_hours"]), 2),
        )
        for _, row in merged.head(10).iterrows()
    ]


def _planned_vs_actual(bundle: DowntimeBundle, task_reports: pd.DataFrame, end_date: date) -> list[PlannedActualPoint]:
    analysis = bundle.analysis
    start_window = pd.Timestamp(end_date) - pd.Timedelta(days=29)
    days = pd.date_range(start=start_window.normalize(), end=pd.Timestamp(end_date).normalize(), freq="D")

    planned = pd.Series(0.0, index=days)
    actual = pd.Series(0.0, index=days)

    if not analysis.empty:
        planned_mask = analysis["type"].astype(str).str.contains("plān|planned", case=False, regex=True)
        planned_group = (
            analysis.loc[planned_mask]
            .assign(day=analysis.loc[planned_mask, "start_date"].dt.floor("D"))
            .groupby("day")["duration_hours"]
            .sum()
        )
        planned.update(planned_group)

    if not task_reports.empty and "report_date" in task_reports.columns:
        actual_group = (
            task_reports.dropna(subset=["report_date"])
            .assign(day=task_reports.dropna(subset=["report_date"])["report_date"].dt.floor("D"))
            .groupby("day")["total_hours"]
            .sum()
        )
        actual.update(actual_group)

    return [
        PlannedActualPoint(
            period=day.strftime("%d-%b"),
            planned=round(float(planned.loc[day]), 2),
            actual=round(float(actual.loc[day]), 2),
        )
        for day in days
    ]


def _mix_trend(bundle: DowntimeBundle) -> list[MixPoint]:
    analysis = bundle.analysis
    if analysis.empty:
        return []

    frame = analysis.assign(
        period=analysis["start_date"].dt.to_period("M").astype(str),
        is_planned=analysis["type"].astype(str).str.contains("plān|planned", case=False, regex=True),
        known=analysis["cat_name"] != "Nav norādīts",
    )
    periods = sorted(frame["period"].dropna().unique().tolist())[-12:]

    points: list[MixPoint] = []
    for period in periods:
        rows = frame[frame["period"] == period]
        total = float(rows["duration_hours"].sum()) or 1.0
        planned = float(rows.loc[rows["is_planned"], "duration_hours"].sum()) / total * 100.0
        unplanned = float(rows.loc[~rows["is_planned"], "duration_hours"].sum()) / total * 100.0
        quality = float(rows["known"].mean()) * 100.0
        points.append(
            MixPoint(
                period=period,
                planned=round(planned, 2),
                unplanned=round(unplanned, 2),
                quality=round(quality, 2),
            )
        )
    return points


def _work_hours_12m(task_reports: pd.DataFrame) -> list[TrendPoint]:
    if task_reports.empty or "report_date" not in task_reports.columns:
        return []

    frame = task_reports.dropna(subset=["report_date"]).copy()
    if frame.empty:
        return []

    grouped = (
        frame.assign(period=frame["report_date"].dt.to_period("M").astype(str))
        .groupby("period", as_index=False)["total_hours"]
        .sum()
        .sort_values("period")
        .tail(12)
    )
    return [
        TrendPoint(period=str(row["period"]), value=round(float(row["total_hours"]), 2))
        for _, row in grouped.iterrows()
    ]


def build_operations_window_payload(
    locale: str,
    bundle: DowntimeBundle,
    task_reports: pd.DataFrame,
    start_date: date,
    end_date: date,
) -> OperationsWindowResponse:
    selected_line_count = int(bundle.filtered["line"].nunique()) if not bundle.filtered.empty else 1
    spark_metrics = [
        _availability_metrics(bundle, selected_line_count, start_date, end_date),
        _event_rate_metrics(bundle, start_date, end_date),
        _mttr_metric(bundle),
        _mtbf_metric(bundle),
        _planned_share_metric(bundle),
        _quality_metric(bundle),
    ]

    return OperationsWindowResponse(
        locale=locale,  # type: ignore[arg-type]
        spark_metrics=spark_metrics,
        task_status=_task_status(bundle, end_date),
        problem_devices=_problem_devices(bundle),
        open_downtimes=_open_downtimes(bundle, task_reports, end_date),
        planned_vs_actual=_planned_vs_actual(bundle, task_reports, end_date),
        mix_trend=_mix_trend(bundle),
        work_hours_12m=_work_hours_12m(task_reports),
    )
