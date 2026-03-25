from __future__ import annotations

from datetime import date

import pandas as pd

from backend.app.domain.line_mapping import extract_line, ordered_lines
from backend.app.domain.models import (
    KpiMetric,
    Locale,
    NamedMetric,
    TechniciansResponse,
    TechnicianWorkRow,
    WorkReportsResponse,
)


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
    for cost_column in (
        "total_cost",
        "extra_total_cost",
        "spares_total_cost",
        "retail_total_cost",
        "retail_extra_total_cost",
        "retail_spares_total_cost",
        "retail_with_vat_total_cost",
        "retail_with_vat_extra_total_cost",
        "retail_with_vat_spares_total_cost",
    ):
        if cost_column in df.columns:
            df[cost_column] = pd.to_numeric(df[cost_column], errors="coerce").fillna(0)
        else:
            df[cost_column] = 0.0
    for column in ("completed_date", "created_date", "date"):
        if column in df.columns:
            df["report_date"] = pd.to_datetime(df[column], errors="coerce")
            break
    if "report_date" not in df.columns:
        df["report_date"] = pd.NaT
    df["report_date"] = df["report_date"].dt.tz_localize(None)
    return df


def _split_technicians(raw_value: str) -> list[str]:
    text = str(raw_value or "").strip()
    if not text or text == "Nav norādīts":
        return ["Nav norādīts"]

    separators = [";", "\n", "|"]
    for separator in separators:
        text = text.replace(separator, ",")

    items = [part.strip() for part in text.split(",")]
    normalized = [item for item in items if item]
    return normalized or ["Nav norādīts"]


def expand_task_reports_by_technician(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    expanded_rows: list[dict] = []
    for _, row in df.iterrows():
        technicians = _split_technicians(str(row.get("user_name_list", "")))
        share = float(row.get("total_hours", 0) or 0) / max(len(technicians), 1)

        for technician in technicians:
            expanded_rows.append(
                {
                    "technician_name": technician,
                    "report_id": row.get("report_id"),
                    "report_nr": row.get("report_nr", "Nav norādīts"),
                    "service_name": row.get("service_name", "Nav norādīts"),
                    "device_name": row.get("device_name", "Nav norādīts"),
                    "line": row.get("report_line", "Nav norādīts"),
                    "report_date": row.get("report_date"),
                    "allocated_hours": share,
                    "source_total_hours": float(row.get("total_hours", 0) or 0),
                }
            )

    expanded = pd.DataFrame(expanded_rows)
    if expanded.empty:
        return expanded

    expanded["allocated_hours"] = pd.to_numeric(expanded["allocated_hours"], errors="coerce").fillna(0)
    expanded["source_total_hours"] = pd.to_numeric(expanded["source_total_hours"], errors="coerce").fillna(0)
    expanded["report_date"] = pd.to_datetime(expanded.get("report_date"), errors="coerce")
    expanded["report_date"] = expanded["report_date"].dt.tz_localize(None)
    return expanded


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


def build_technicians_payload(
    locale: Locale,
    df: pd.DataFrame,
    selected_technician: str | None,
) -> TechniciansResponse:
    expanded = expand_task_reports_by_technician(df)
    if expanded.empty:
        return TechniciansResponse(
            locale=locale,
            kpis=[
                KpiMetric(id="technicians", label="Technicians", value=0),
                KpiMetric(id="reports", label="Reports", value=0),
                KpiMetric(id="hours", label="Hours", value=0, unit="h"),
                KpiMetric(id="avg_hours", label="Avg hours/person", value=0, unit="h"),
            ],
            selected_technician=selected_technician,
            technician_hours=[],
            technician_reports=[],
            service_breakdown=[],
            device_breakdown=[],
            line_breakdown=[],
            rows=[],
        )

    technician_hours = (
        expanded.groupby("technician_name", as_index=False)["allocated_hours"]
        .sum()
        .sort_values("allocated_hours", ascending=False)
    )
    technician_reports = (
        expanded.groupby("technician_name", as_index=False)["report_nr"]
        .nunique()
        .rename(columns={"report_nr": "reports"})
        .sort_values("reports", ascending=False)
    )

    focus_name = selected_technician or str(technician_hours.iloc[0]["technician_name"])
    focused = expanded[expanded["technician_name"] == focus_name].copy()
    if focused.empty:
        focus_name = str(technician_hours.iloc[0]["technician_name"])
        focused = expanded[expanded["technician_name"] == focus_name].copy()

    service_breakdown = (
        focused.groupby("service_name", as_index=False)["allocated_hours"]
        .sum()
        .sort_values("allocated_hours", ascending=False)
        .head(10)
    )
    device_breakdown = (
        focused.groupby("device_name", as_index=False)["allocated_hours"]
        .sum()
        .sort_values("allocated_hours", ascending=False)
        .head(10)
    )
    line_breakdown = (
        focused.groupby("line", as_index=False)["allocated_hours"]
        .sum()
        .sort_values("allocated_hours", ascending=False)
        .head(10)
    )
    focused_rows = (
        focused.sort_values(["report_date", "report_nr"], ascending=[False, False])
        .head(40)
    )

    total_allocated_hours = float(expanded["allocated_hours"].sum())
    avg_hours = total_allocated_hours / max(len(technician_hours), 1)

    return TechniciansResponse(
        locale=locale,
        kpis=[
            KpiMetric(id="technicians", label="Technicians", value=int(len(technician_hours))),
            KpiMetric(id="reports", label="Reports", value=int(expanded["report_nr"].nunique())),
            KpiMetric(id="hours", label="Allocated hours", value=round(total_allocated_hours, 1), unit="h"),
            KpiMetric(id="avg_hours", label="Avg hours/person", value=round(avg_hours, 1), unit="h"),
        ],
        selected_technician=focus_name,
        technician_hours=[
            NamedMetric(name=str(row["technician_name"]), value=round(float(row["allocated_hours"]), 2))
            for _, row in technician_hours.head(30).iterrows()
        ],
        technician_reports=[
            NamedMetric(name=str(row["technician_name"]), value=float(row["reports"]))
            for _, row in technician_reports.head(30).iterrows()
        ],
        service_breakdown=[
            NamedMetric(name=str(row["service_name"]), value=round(float(row["allocated_hours"]), 2))
            for _, row in service_breakdown.iterrows()
        ],
        device_breakdown=[
            NamedMetric(name=str(row["device_name"]), value=round(float(row["allocated_hours"]), 2))
            for _, row in device_breakdown.iterrows()
        ],
        line_breakdown=[
            NamedMetric(name=str(row["line"]), value=round(float(row["allocated_hours"]), 2))
            for _, row in line_breakdown.iterrows()
        ],
        rows=[
            TechnicianWorkRow(
                technician_name=str(row["technician_name"]),
                report_nr=str(row["report_nr"]),
                service_name=str(row["service_name"]),
                device_name=str(row["device_name"]),
                line=str(row["line"]),
                report_date=row["report_date"].isoformat() if pd.notna(row["report_date"]) else None,
                allocated_hours=round(float(row["allocated_hours"]), 2),
                source_total_hours=round(float(row["source_total_hours"]), 2),
            )
            for _, row in focused_rows.iterrows()
        ],
    )
