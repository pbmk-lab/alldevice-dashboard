from __future__ import annotations

from datetime import date

import pandas as pd

from backend.app.domain.line_mapping import extract_line, ordered_lines
from backend.app.domain.models import KpiMetric, Locale, NamedMetric, WorkReportsResponse


def normalize_task_report_rows(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["total_time_seconds"] = pd.to_numeric(
        df.get("total_time_seconds"), errors="coerce"
    ).fillna(0)
    df["total_hours"] = df["total_time_seconds"] / 3600
    df["service_name"] = df.get("service_name", "").fillna("Nav norādīts")
    df["device_name"] = df.get("device_name", "").fillna("Nav norādīts")
    df["device_location"] = df.get("device_location", "").fillna("Nav norādīts")
    df["user_name_list"] = df.get("user_name_list", "").fillna("Nav norādīts")
    df["report_nr"] = df.get("report_nr", "").fillna("Nav norādīts")
    df["report_line"] = df["device_location"].apply(extract_line)
    for column in ("completed_date", "created_date", "date"):
        if column in df.columns:
            df["report_date"] = pd.to_datetime(df[column], errors="coerce")
            break
    if "report_date" not in df.columns:
        df["report_date"] = pd.NaT
    df["report_date"] = df["report_date"].dt.tz_localize(None)
    return df


def filter_task_reports(
    df: pd.DataFrame,
    selected_lines: list[str] | None,
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    if df.empty:
        return df
    selected = selected_lines or ordered_lines()
    start_filter = pd.Timestamp(start_date)
    end_filter = pd.Timestamp(end_date).replace(hour=23, minute=59, second=59)
    return df[
        (df["report_line"].isin(selected))
        & (
            df["report_date"].isna()
            | (
                (df["report_date"] >= start_filter)
                & (df["report_date"] <= end_filter)
            )
        )
    ].copy()


def build_work_reports_payload(
    locale: Locale,
    df: pd.DataFrame,
    total_reports_api: int,
) -> WorkReportsResponse:
    if df.empty:
        return WorkReportsResponse(
            locale=locale,
            kpis=[
                KpiMetric(id="reports", label="Reports", value=0),
                KpiMetric(id="api_reports", label="API Reports", value=total_reports_api),
                KpiMetric(id="hours", label="Hours", value=0, unit="h"),
                KpiMetric(id="avg_hours", label="Avg hours/report", value=0, unit="h"),
            ],
            technician_hours=[],
            service_hours=[],
            line_hours=[],
            raw_rows=[],
        )

    total_reports = len(df)
    total_hours = float(df["total_hours"].sum())
    avg_report_hours = float(df["total_hours"].mean()) if total_reports else 0.0

    technician_hours = (
        df.groupby("user_name_list", as_index=False)["total_hours"]
        .sum()
        .sort_values("total_hours", ascending=False)
        .head(10)
    )
    service_hours = (
        df.groupby("service_name", as_index=False)["total_hours"]
        .sum()
        .sort_values("total_hours", ascending=False)
        .head(10)
    )
    line_hours = (
        df.groupby("report_line", as_index=False)["total_hours"]
        .sum()
        .sort_values("total_hours", ascending=False)
        .head(10)
    )

    return WorkReportsResponse(
        locale=locale,
        kpis=[
            KpiMetric(id="reports", label="Reports", value=total_reports),
            KpiMetric(id="api_reports", label="API Reports", value=total_reports_api),
            KpiMetric(id="hours", label="Hours", value=round(total_hours, 1), unit="h"),
            KpiMetric(
                id="avg_hours",
                label="Avg hours/report",
                value=round(avg_report_hours, 2),
                unit="h",
            ),
        ],
        technician_hours=[
            NamedMetric(name=str(row["user_name_list"]), value=round(float(row["total_hours"]), 2))
            for _, row in technician_hours.iterrows()
        ],
        service_hours=[
            NamedMetric(name=str(row["service_name"]), value=round(float(row["total_hours"]), 2))
            for _, row in service_hours.iterrows()
        ],
        line_hours=[
            NamedMetric(name=str(row["report_line"]), value=round(float(row["total_hours"]), 2))
            for _, row in line_hours.iterrows()
        ],
        raw_rows=df.to_dict(orient="records"),
    )
