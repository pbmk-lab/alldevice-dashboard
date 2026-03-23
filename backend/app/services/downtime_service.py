from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd

from backend.app.core.config import Settings
from backend.app.core.i18n import t
from backend.app.domain.line_mapping import extract_line, ordered_lines
from backend.app.domain.models import (
    AlertItem,
    DataQualityResponse,
    DeviceRow,
    DevicesResponse,
    FiltersResponse,
    KpiMetric,
    Locale,
    NamedMetric,
    OverviewResponse,
    RecommendationItem,
    TrendPoint,
    TriageLineRow,
    TriageResponse,
)


@dataclass
class DowntimeBundle:
    filtered: pd.DataFrame
    analysis: pd.DataFrame
    closed: pd.DataFrame
    failures: pd.DataFrame
    excluded_anomalies: int
    excluded_anomaly_hours: float


def classify_type(cat_name: str, locale: Locale) -> str:
    cat_upper = str(cat_name).upper()
    if "PLĀNOTS" in cat_upper:
        return t(locale, "type_planned")
    return t(locale, "type_unplanned")


def normalize_downtime_rows(rows: list[dict], locale: Locale) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["start_date"] = pd.to_datetime(df.get("start_date"), errors="coerce")
    df["end_date"] = pd.to_datetime(df.get("end_date"), errors="coerce")
    df["duration_seconds"] = pd.to_numeric(
        df.get("duration_seconds"), errors="coerce"
    ).fillna(0)
    df["duration_hours"] = df["duration_seconds"] / 3600
    df["month"] = df["start_date"].dt.to_period("M").astype(str)
    df["cat_name"] = df.get("cat_name", "").fillna("").replace("", "Nav norādīts")
    df["device_name"] = df.get("device_name", "").fillna("Nav norādīts")
    df["device_location"] = df.get("device_location", "").fillna("Nav norādīts")
    df["comments"] = df.get("comments", "").fillna("")
    df["is_ended"] = df.get("is_ended", False).fillna(False)
    df["line"] = df["device_location"].apply(extract_line)
    df["type"] = df["cat_name"].apply(lambda value: classify_type(value, locale))
    df["start_date"] = df["start_date"].dt.tz_localize(None)
    return df


def build_filters_payload(df: pd.DataFrame, settings: Settings) -> FiltersResponse:
    min_date = df["start_date"].min()
    max_date = df["start_date"].max()
    if pd.isna(min_date) or pd.isna(max_date):
        min_date = pd.Timestamp(settings.default_date_start)
        max_date = pd.Timestamp(settings.default_date_end)
    return FiltersResponse(
        lines=ordered_lines(),
        min_date=min_date.date(),
        max_date=max_date.date(),
        default_start=min_date.date(),
        default_end=max_date.date(),
        default_locale=settings.default_locale,  # type: ignore[arg-type]
    )


def build_bundle(
    df: pd.DataFrame,
    selected_lines: list[str] | None,
    start_date: date,
    end_date: date,
    analysis_max_hours: int,
) -> DowntimeBundle:
    if df.empty:
        empty = pd.DataFrame()
        return DowntimeBundle(empty, empty, empty, empty, 0, 0.0)

    selected = selected_lines or ordered_lines()
    start_filter = pd.Timestamp(start_date)
    end_filter = pd.Timestamp(end_date).replace(hour=23, minute=59, second=59)

    filtered = df[
        (df["line"].isin(selected))
        & (df["start_date"] >= start_filter)
        & (df["start_date"] <= end_filter)
    ].copy()
    if filtered.empty:
        empty = pd.DataFrame()
        return DowntimeBundle(empty, empty, empty, empty, 0, 0.0)

    filtered["month"] = filtered["start_date"].dt.to_period("M").astype(str)
    filtered["is_anomaly"] = filtered["duration_hours"] > analysis_max_hours
    analysis = filtered[
        (filtered["duration_hours"] >= 0)
        & (filtered["duration_hours"] <= analysis_max_hours)
    ].copy()

    if analysis.empty:
        empty = pd.DataFrame()
        return DowntimeBundle(
            filtered,
            empty,
            empty,
            empty,
            int(filtered["is_anomaly"].sum()),
            float(filtered.loc[filtered["is_anomaly"], "duration_hours"].sum()),
        )

    closed = analysis[
        (analysis["is_ended"] == True)
        & (analysis["duration_hours"] > 0)
        & (analysis["duration_hours"] < 24)
    ].copy()

    failures = analysis.sort_values("start_date").copy()
    if len(failures) > 1:
        failures["prev_start"] = failures["start_date"].shift(1)
        failures["mtbf_hours"] = (
            (failures["start_date"] - failures["prev_start"]).dt.total_seconds() / 3600
        )
    else:
        failures["mtbf_hours"] = pd.NA

    return DowntimeBundle(
        filtered=filtered,
        analysis=analysis,
        closed=closed,
        failures=failures,
        excluded_anomalies=int(filtered["is_anomaly"].sum()),
        excluded_anomaly_hours=float(
            filtered.loc[filtered["is_anomaly"], "duration_hours"].sum()
        ),
    )


def calculate_kpis(analysis: pd.DataFrame, closed: pd.DataFrame, failures: pd.DataFrame) -> dict[str, float | int]:
    mttr = float(closed["duration_hours"].mean()) if not closed.empty else 0.0
    mtbf = (
        float(failures["mtbf_hours"].dropna().mean())
        if not failures.empty and failures["mtbf_hours"].dropna().any()
        else 0.0
    )
    return {
        "mttr": mttr,
        "mtbf": mtbf,
        "total_downtime_hours": float(analysis["duration_hours"].sum()) if not analysis.empty else 0.0,
        "total_events": int(len(analysis)),
    }


def monthly_trend(frame: pd.DataFrame, value_column: str) -> list[TrendPoint]:
    if frame.empty:
        return []
    grouped = (
        frame.groupby("month", as_index=False)[value_column]
        .mean()
        .sort_values("month")
    )
    return [
        TrendPoint(period=str(row["month"]), value=float(row[value_column]))
        for _, row in grouped.iterrows()
    ]


def _build_alerts(
    locale: Locale,
    missing_pct: float,
    mttr: float,
    excluded_anomalies: int,
    analysis_max_hours: int,
) -> list[AlertItem]:
    alerts: list[AlertItem] = []
    if missing_pct > 30:
        alerts.append(
            AlertItem(
                id="missing-critical",
                severity="critical",
                title=t(locale, "alert_missing_critical_title"),
                description=t(locale, "alert_missing_critical_desc", value=missing_pct),
            )
        )
    elif missing_pct > 10:
        alerts.append(
            AlertItem(
                id="missing-warning",
                severity="warning",
                title=t(locale, "alert_missing_warning_title"),
                description=t(locale, "alert_missing_warning_desc", value=missing_pct),
            )
        )
    if mttr > 5:
        alerts.append(
            AlertItem(
                id="mttr",
                severity="critical" if mttr > 10 else "warning",
                title=t(locale, "alert_mttr_title"),
                description=t(locale, "alert_mttr_desc", value=mttr),
            )
        )
    if excluded_anomalies > 0:
        alerts.append(
            AlertItem(
                id="anomalies",
                severity="info",
                title=t(locale, "alert_anomaly_title"),
                description=t(
                    locale,
                    "alert_anomaly_desc",
                    count=excluded_anomalies,
                    hours=analysis_max_hours,
                ),
            )
        )
    return alerts


def _build_recommendations(locale: Locale, analysis: pd.DataFrame) -> list[RecommendationItem]:
    if analysis.empty:
        return []

    rows = (
        analysis.groupby("cat_name", as_index=False)["duration_hours"]
        .sum()
        .sort_values("duration_hours", ascending=False)
        .head(5)
    )
    recommendations: list[RecommendationItem] = []
    for index, row in rows.iterrows():
        cause = str(row["cat_name"]).upper()
        if "STOP" in cause:
            title_key = "rec_stop_title"
            desc_key = "rec_stop_desc"
        elif "NAV NORĀDĪTS" in cause:
            title_key = "rec_missing_title"
            desc_key = "rec_missing_desc"
        elif "PLĀNOTS" in cause:
            title_key = "rec_planned_title"
            desc_key = "rec_planned_desc"
        else:
            title_key = "rec_default_title"
            desc_key = "rec_default_desc"
        recommendations.append(
            RecommendationItem(
                id=f"rec-{index}",
                title=f"{row['cat_name']}: {t(locale, title_key)}",
                description=t(locale, desc_key),
            )
        )
    return recommendations


def build_overview_payload(
    locale: Locale,
    bundle: DowntimeBundle,
    settings: Settings,
) -> OverviewResponse:
    analysis = bundle.analysis
    kpi_values = calculate_kpis(analysis, bundle.closed, bundle.failures)
    missing_category = int((analysis["cat_name"] == "Nav norādīts").sum()) if not analysis.empty else 0
    total_records = int(len(analysis))
    missing_pct = (missing_category / total_records * 100) if total_records else 0.0

    downtime_by_line = (
        analysis.groupby("line", as_index=False)["duration_hours"]
        .sum()
        .sort_values("duration_hours", ascending=False)
        if not analysis.empty
        else pd.DataFrame()
    )
    downtime_by_type = (
        analysis.groupby("type", as_index=False)["duration_hours"]
        .sum()
        .sort_values("duration_hours", ascending=False)
        if not analysis.empty
        else pd.DataFrame()
    )
    downtime_by_device = (
        analysis.groupby("device_name", as_index=False)["duration_hours"]
        .sum()
        .sort_values("duration_hours", ascending=False)
        if not analysis.empty
        else pd.DataFrame()
    )

    top_line = (
        str(downtime_by_line.iloc[0]["line"]) if not downtime_by_line.empty else "-"
    )
    top_device = (
        str(downtime_by_device.iloc[0]["device_name"])
        if not downtime_by_device.empty
        else "-"
    )

    kpis = [
        KpiMetric(id="mttr", label="MTTR", value=round(float(kpi_values["mttr"]), 2), unit="h"),
        KpiMetric(id="mtbf", label="MTBF", value=round(float(kpi_values["mtbf"]), 2), unit="h"),
        KpiMetric(
            id="downtime",
            label="Downtime",
            value=round(float(kpi_values["total_downtime_hours"]), 1),
            unit="h",
        ),
        KpiMetric(id="events", label="Events", value=int(kpi_values["total_events"])),
    ]

    return OverviewResponse(
        locale=locale,
        kpis=kpis,
        alerts=_build_alerts(
            locale,
            missing_pct,
            float(kpi_values["mttr"]),
            bundle.excluded_anomalies,
            settings.analysis_max_hours,
        ),
        recommendations=_build_recommendations(locale, analysis),
        top_line=top_line,
        top_device=top_device,
        mttr_trend=monthly_trend(bundle.closed, "duration_hours"),
        mtbf_trend=monthly_trend(bundle.failures.dropna(subset=["mtbf_hours"]), "mtbf_hours"),
        downtime_by_line=[
            NamedMetric(name=str(row["line"]), value=float(row["duration_hours"]))
            for _, row in downtime_by_line.iterrows()
        ],
        downtime_by_type=[
            NamedMetric(name=str(row["type"]), value=float(row["duration_hours"]))
            for _, row in downtime_by_type.iterrows()
        ],
        quality={
            "missing_category_pct": round(missing_pct, 2),
            "excluded_anomalies": bundle.excluded_anomalies,
            "excluded_anomaly_hours": round(bundle.excluded_anomaly_hours, 2),
        },
    )


def build_triage_payload(locale: Locale, bundle: DowntimeBundle) -> TriageResponse:
    analysis = bundle.analysis
    filtered = bundle.filtered
    if analysis.empty:
        return TriageResponse(locale=locale, rows=[])

    missing = (
        analysis.assign(missing=analysis["cat_name"] == "Nav norādīts")
        .groupby("line")
        .agg(
            downtime_hours=("duration_hours", "sum"),
            events=("duration_hours", "count"),
            avg_event_hours=("duration_hours", "mean"),
            missing=("missing", "sum"),
        )
        .reset_index()
    )
    totals = (
        filtered.groupby("line", as_index=False)["is_anomaly"]
        .sum()
        .rename(columns={"is_anomaly": "anomaly_count"})
    )
    top_categories = (
        analysis.groupby(["line", "cat_name"], as_index=False)["duration_hours"]
        .sum()
        .sort_values(["line", "duration_hours"], ascending=[True, False])
        .drop_duplicates("line")
        .rename(columns={"cat_name": "top_category"})
    )
    merged = missing.merge(totals, on="line", how="left").merge(
        top_categories[["line", "top_category"]], on="line", how="left"
    )
    merged["anomaly_count"] = merged["anomaly_count"].fillna(0).astype(int)
    merged["missing_pct"] = (merged["missing"] / merged["events"]) * 100
    merged["risk_score"] = (
        merged["downtime_hours"] * 0.6
        + merged["missing_pct"] * 1.5
        + merged["anomaly_count"] * 20
    )

    def priority(score: float) -> str:
        if score > 500:
            return t(locale, "priority_high")
        if score > 120:
            return t(locale, "priority_medium")
        return t(locale, "priority_low")

    merged["priority"] = merged["risk_score"].apply(priority)
    merged = merged.sort_values("risk_score", ascending=False)

    return TriageResponse(
        locale=locale,
        rows=[
            TriageLineRow(
                line=str(row["line"]),
                downtime_hours=round(float(row["downtime_hours"]), 2),
                events=int(row["events"]),
                avg_event_hours=round(float(row["avg_event_hours"]), 2),
                missing_pct=round(float(row["missing_pct"]), 2),
                anomaly_count=int(row["anomaly_count"]),
                priority=str(row["priority"]),
                risk_score=round(float(row["risk_score"]), 2),
                top_category=str(row.get("top_category", "Nav norādīts")),
            )
            for _, row in merged.iterrows()
        ],
    )


def build_devices_payload(
    locale: Locale,
    bundle: DowntimeBundle,
    line: str | None,
) -> DevicesResponse:
    analysis = bundle.analysis
    if line:
        analysis = analysis[analysis["line"] == line].copy()

    if analysis.empty:
        return DevicesResponse(
            locale=locale,
            selected_line=line,
            top_devices=[],
            category_breakdown=[],
            monthly_top_device_trend=[],
        )

    top_devices = (
        analysis.groupby(["device_name", "line"], as_index=False)
        .agg(
            downtime_hours=("duration_hours", "sum"),
            events=("duration_hours", "count"),
            avg_event_hours=("duration_hours", "mean"),
        )
        .sort_values("downtime_hours", ascending=False)
        .head(10)
    )
    category_breakdown = (
        analysis.groupby("cat_name", as_index=False)["duration_hours"]
        .sum()
        .sort_values("duration_hours", ascending=False)
        .head(10)
    )
    leading_device = str(top_devices.iloc[0]["device_name"])
    trend = (
        analysis[analysis["device_name"] == leading_device]
        .groupby("month", as_index=False)["duration_hours"]
        .sum()
        .sort_values("month")
    )

    return DevicesResponse(
        locale=locale,
        selected_line=line,
        top_devices=[
            DeviceRow(
                device_name=str(row["device_name"]),
                line=str(row["line"]),
                downtime_hours=round(float(row["downtime_hours"]), 2),
                events=int(row["events"]),
                avg_event_hours=round(float(row["avg_event_hours"]), 2),
            )
            for _, row in top_devices.iterrows()
        ],
        category_breakdown=[
            NamedMetric(name=str(row["cat_name"]), value=round(float(row["duration_hours"]), 2))
            for _, row in category_breakdown.iterrows()
        ],
        monthly_top_device_trend=[
            TrendPoint(period=str(row["month"]), value=round(float(row["duration_hours"]), 2))
            for _, row in trend.iterrows()
        ],
    )


def build_quality_payload(locale: Locale, bundle: DowntimeBundle) -> DataQualityResponse:
    analysis = bundle.analysis
    filtered = bundle.filtered
    if analysis.empty:
        return DataQualityResponse(
            locale=locale,
            missing_category_pct=0,
            excluded_anomalies=bundle.excluded_anomalies,
            excluded_anomaly_hours=round(bundle.excluded_anomaly_hours, 2),
            quality_by_line=[],
            anomaly_distribution=[],
        )

    missing_category = int((analysis["cat_name"] == "Nav norādīts").sum())
    missing_pct = (missing_category / len(analysis) * 100) if len(analysis) else 0.0
    quality_by_line = (
        analysis.assign(missing=analysis["cat_name"] == "Nav norādīts")
        .groupby("line")
        .agg(total=("cat_name", "count"), missing=("missing", "sum"))
        .reset_index()
    )
    quality_by_line["missing_pct"] = (
        quality_by_line["missing"] / quality_by_line["total"] * 100
    )
    quality_by_line = quality_by_line.sort_values("missing_pct", ascending=False)
    anomaly_distribution = (
        filtered.groupby("line", as_index=False)["is_anomaly"]
        .sum()
        .rename(columns={"is_anomaly": "count"})
        .sort_values("count", ascending=False)
    )

    return DataQualityResponse(
        locale=locale,
        missing_category_pct=round(missing_pct, 2),
        excluded_anomalies=bundle.excluded_anomalies,
        excluded_anomaly_hours=round(bundle.excluded_anomaly_hours, 2),
        quality_by_line=[
            NamedMetric(
                name=str(row["line"]),
                value=round(float(row["missing_pct"]), 2),
                meta={
                    "total": int(row["total"]),
                    "missing": int(row["missing"]),
                },
            )
            for _, row in quality_by_line.iterrows()
        ],
        anomaly_distribution=[
            NamedMetric(name=str(row["line"]), value=float(row["count"]))
            for _, row in anomaly_distribution.iterrows()
        ],
    )
