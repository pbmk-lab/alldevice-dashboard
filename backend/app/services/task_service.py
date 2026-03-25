from __future__ import annotations

from datetime import date

import pandas as pd

from backend.app.domain.line_mapping import extract_line, ordered_lines
from backend.app.domain.models import (
    CostBreakdownPoint,
    CostsResponse,
    KpiMetric,
    Locale,
    NamedMetric,
    TaskBoardResponse,
    TaskMixPoint,
    TaskBoardRow,
    TrendPoint,
)


def normalize_task_rows(rows: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["task_id"] = pd.to_numeric(df.get("task_id"), errors="coerce").fillna(0).astype(int)
    df["task_number_combined"] = df.get("task_number_combined", "").fillna("").replace("", "—")
    df["device_name"] = df.get("device_name", "").fillna("Nav norādīts")
    df["service_name"] = df.get("service_name", "").fillna("Nav norādīts")
    df["priority_name"] = df.get("priority_name", "").fillna("normal")
    df["task_status"] = df.get("task_status", "").fillna("")
    df["service_type"] = df.get("service_type", "").fillna("")
    df["service_date"] = pd.to_datetime(df.get("service_date"), errors="coerce")
    df["created_on"] = pd.to_datetime(df.get("created_on"), errors="coerce")
    df["overdue"] = pd.to_numeric(df.get("overdue"), errors="coerce").fillna(0).astype(int)
    def parse_duration_hours(value: object) -> float:
        if value in (None, "", "0000-00-00"):
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip()
        if ":" in text:
            parts = text.split(":")
            if len(parts) >= 2:
                try:
                    return int(parts[0]) + int(parts[1]) / 60
                except ValueError:
                    return 0.0
        try:
            return float(text)
        except ValueError:
            return 0.0

    if "service_duration" in df.columns:
        df["service_duration_hours"] = df["service_duration"].apply(parse_duration_hours)
    else:
        df["service_duration_hours"] = 0.0
    if "device_location" in df.columns:
        df["line"] = df["device_location"].fillna("").apply(extract_line)
    elif "object_id" in df.columns:
        df["line"] = "Cits"
    else:
        df["line"] = "Cits"

    def parse_users(value: object) -> list[str]:
        if isinstance(value, list):
            names: list[str] = []
            for item in value:
                if isinstance(item, dict):
                    name = str(
                        item.get("name")
                        or item.get("user_name")
                        or item.get("fullname")
                        or item.get("full_name")
                        or ""
                    ).strip()
                    if name:
                        names.append(name)
            return names
        return []

    def used_spares_cost(value: object) -> float:
        if not isinstance(value, list):
            return 0.0
        total = 0.0
        for item in value:
            if not isinstance(item, dict):
                continue
            total += float(item.get("cost_total_price") or item.get("retail_total_price") or 0)
        return total

    if "users" in df.columns:
        df["assigned_users"] = df["users"].apply(parse_users)
    else:
        df["assigned_users"] = [[] for _ in range(len(df))]
    if "used_spares" in df.columns:
        df["spares_cost"] = df["used_spares"].apply(used_spares_cost)
    else:
        df["spares_cost"] = 0.0
    return df


def filter_tasks(
    df: pd.DataFrame,
    selected_lines: list[str] | None,
    start_date: date,
    end_date: date,
) -> pd.DataFrame:
    if df.empty:
        return df
    selected = selected_lines or ordered_lines()
    if "line" not in df.columns or df["line"].eq("Cits").all():
        return df.copy()
    start_filter = pd.Timestamp(start_date)
    end_filter = pd.Timestamp(end_date).replace(hour=23, minute=59, second=59)

    due_date = df["service_date"].fillna(df["created_on"])
    return df[
        (df["line"].isin(selected))
        & (
            due_date.isna()
            | ((due_date >= start_filter) & (due_date <= end_filter))
        )
    ].copy()


def build_task_board_payload(locale: Locale, df: pd.DataFrame) -> TaskBoardResponse:
    if df.empty:
        return TaskBoardResponse(
            locale=locale,
            kpis=[
                KpiMetric(id="open_tasks", label="Open tasks", value=0),
                KpiMetric(id="overdue_tasks", label="Overdue", value=0),
                KpiMetric(id="high_priority", label="High priority", value=0),
                KpiMetric(id="estimated_hours", label="Estimated", value=0, unit="h"),
            ],
            status_buckets=[],
            priority_breakdown=[],
            service_type_breakdown=[],
            overdue_trend=[],
            distribution_trend=[],
            rows=[],
        )

    reference_date = pd.Timestamp.now().normalize()
    high_priority = int(df["priority_name"].astype(str).str.contains("high", case=False).sum())
    overdue_tasks = int((df["overdue"] > 0).sum())
    estimated_hours = float(df["service_duration_hours"].sum())
    due_date = df["service_date"].fillna(df["created_on"])
    today_tasks = int((due_date.dt.normalize() == reference_date).sum())
    pending_tasks = max(len(df) - overdue_tasks - today_tasks, 0)

    priority_breakdown = (
        df.groupby("priority_name", as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values("count", ascending=False)
    )
    service_type_breakdown = (
        df.groupby("service_type", as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values("count", ascending=False)
    )
    overdue_trend = (
        df.assign(period=df["service_date"].fillna(df["created_on"]).dt.to_period("M").astype(str))
        .groupby("period", as_index=False)["overdue"]
        .mean()
        .sort_values("period")
    )

    def classify_status_bucket(row: pd.Series) -> str:
        row_due = row.get("service_date")
        if pd.notna(row.get("overdue")) and float(row.get("overdue") or 0) > 0:
            return "Overdue"
        if pd.notna(row_due) and pd.Timestamp(row_due).normalize() == reference_date:
            return "Today"
        return "In progress"

    def classify_distribution_bucket(row: pd.Series) -> str:
        raw = " ".join(
            [
                str(row.get("service_type") or ""),
                str(row.get("service_name") or ""),
                str(row.get("task_status") or ""),
            ]
        ).lower()
        if any(token in raw for token in ("ārkārt", "avārij", "emergency", "urgent", "breakdown")):
            return "emergency"
        if any(token in raw for token in ("plān", "planned", "pm", "prevent", "schedule")):
            return "planned"
        return "regular"

    distribution = df.copy()
    distribution["distribution_bucket"] = distribution.apply(classify_distribution_bucket, axis=1)
    distribution["period"] = due_date.dt.to_period("M").astype(str)
    grouped_distribution = (
        distribution.groupby(["period", "distribution_bucket"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values("period")
    )

    distribution_trend: list[TaskMixPoint] = []
    for period, group in grouped_distribution.groupby("period"):
        total = float(group["count"].sum()) or 1.0
        values = {str(row["distribution_bucket"]): float(row["count"]) / total * 100.0 for _, row in group.iterrows()}
        distribution_trend.append(
            TaskMixPoint(
                period=str(period),
                emergency=round(values.get("emergency", 0.0), 2),
                planned=round(values.get("planned", 0.0), 2),
                regular=round(values.get("regular", 0.0), 2),
            )
        )

    rows = (
        df.sort_values(["overdue", "priority_name", "service_date"], ascending=[False, False, True])
        .head(50)
    )

    return TaskBoardResponse(
        locale=locale,
        kpis=[
            KpiMetric(id="open_tasks", label="Open tasks", value=int(len(df))),
            KpiMetric(id="overdue_tasks", label="Overdue", value=overdue_tasks),
            KpiMetric(id="high_priority", label="High priority", value=high_priority),
            KpiMetric(id="estimated_hours", label="Estimated", value=round(estimated_hours, 1), unit="h"),
        ],
        status_buckets=[
            NamedMetric(name="Overdue", value=float(overdue_tasks)),
            NamedMetric(name="Today", value=float(today_tasks)),
            NamedMetric(name="In progress", value=float(pending_tasks)),
        ],
        priority_breakdown=[
            NamedMetric(name=str(row["priority_name"] or "normal"), value=float(row["count"]))
            for _, row in priority_breakdown.iterrows()
        ],
        service_type_breakdown=[
            NamedMetric(name=str(row["service_type"] or "unknown"), value=float(row["count"]))
            for _, row in service_type_breakdown.iterrows()
        ],
        overdue_trend=[
            TrendPoint(period=str(row["period"]), value=round(float(row["overdue"]), 2))
            for _, row in overdue_trend.iterrows()
        ],
        distribution_trend=distribution_trend,
        rows=[
            TaskBoardRow(
                task_id=int(row["task_id"]),
                task_number=str(row["task_number_combined"]),
                device_name=str(row["device_name"]),
                service_name=str(row["service_name"]),
                line=str(row["line"]),
                priority=str(row["priority_name"] or "normal"),
                overdue_pct=int(row["overdue"]),
                due_date=row["service_date"].strftime("%d.%m.%Y") if pd.notna(row["service_date"]) else None,
                task_status=str(row["task_status"] or ""),
                status_bucket=classify_status_bucket(row),
                service_type=str(row["service_type"] or ""),
                assigned_users=[str(item) for item in row["assigned_users"]],
                estimated_hours=round(float(row["service_duration_hours"]), 2),
                spares_cost=round(float(row["spares_cost"]), 2),
            )
            for _, row in rows.iterrows()
        ],
    )


def build_costs_payload(locale: Locale, df: pd.DataFrame) -> CostsResponse:
    if df.empty:
        return CostsResponse(
            locale=locale,
            kpis=[
                KpiMetric(id="total_cost", label="Total cost", value=0),
                KpiMetric(id="extra_cost", label="Extra cost", value=0),
                KpiMetric(id="spares_cost", label="Spares cost", value=0),
                KpiMetric(id="avg_cost", label="Avg report cost", value=0),
            ],
            monthly_total_costs=[],
            monthly_cost_breakdown=[],
            service_costs=[],
            line_costs=[],
        )

    total_cost = float(df["total_cost"].sum())
    extra_cost = float(df["extra_total_cost"].sum())
    spares_cost = float(df["spares_total_cost"].sum())
    avg_cost = total_cost / max(len(df), 1)

    grouped = (
        df.assign(period=df["report_date"].dt.to_period("M").astype(str))
        .groupby("period", as_index=False)
        .agg(
            total_cost=("total_cost", "sum"),
            extra_cost=("extra_total_cost", "sum"),
            spares_cost=("spares_total_cost", "sum"),
            labor_cost=("total_cost", lambda s: max(float(s.sum()) - 0.0, 0.0)),
        )
        .sort_values("period")
    )
    service_costs = (
        df.groupby("service_name", as_index=False)["total_cost"]
        .sum()
        .sort_values("total_cost", ascending=False)
        .head(10)
    )
    line_costs = (
        df.groupby("report_line", as_index=False)["total_cost"]
        .sum()
        .sort_values("total_cost", ascending=False)
        .head(10)
    )

    return CostsResponse(
        locale=locale,
        kpis=[
            KpiMetric(id="total_cost", label="Total cost", value=round(total_cost, 2)),
            KpiMetric(id="extra_cost", label="Extra cost", value=round(extra_cost, 2)),
            KpiMetric(id="spares_cost", label="Spares cost", value=round(spares_cost, 2)),
            KpiMetric(id="avg_cost", label="Avg report cost", value=round(avg_cost, 2)),
        ],
        monthly_total_costs=[
            TrendPoint(period=str(row["period"]), value=round(float(row["total_cost"]), 2))
            for _, row in grouped.iterrows()
        ],
        monthly_cost_breakdown=[
            CostBreakdownPoint(
                period=str(row["period"]),
                labor=round(max(float(row["total_cost"]) - float(row["extra_cost"]) - float(row["spares_cost"]), 0.0), 2),
                extra=round(float(row["extra_cost"]), 2),
                spares=round(float(row["spares_cost"]), 2),
            )
            for _, row in grouped.iterrows()
        ],
        service_costs=[
            NamedMetric(name=str(row["service_name"]), value=round(float(row["total_cost"]), 2))
            for _, row in service_costs.iterrows()
        ],
        line_costs=[
            NamedMetric(name=str(row["report_line"]), value=round(float(row["total_cost"]), 2))
            for _, row in line_costs.iterrows()
        ],
    )
