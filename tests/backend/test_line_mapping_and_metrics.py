from __future__ import annotations

from datetime import date

from backend.app.core.config import Settings
from backend.app.domain.line_mapping import extract_line
from backend.app.services.downtime_service import (
    build_bundle,
    build_filters_payload,
    build_overview_payload,
    calculate_kpis,
    normalize_downtime_rows,
)


SAMPLE_ROWS = [
    {
        "id": 1,
        "start_date": "2025-01-01T08:00:00",
        "end_date": "2025-01-01T10:00:00",
        "duration_seconds": 7200,
        "cat_name": "",
        "device_name": "Press A",
        "device_location": "1 LĪNIJA ZONA",
        "comments": "",
        "is_ended": True,
    },
    {
        "id": 2,
        "start_date": "2025-01-03T08:00:00",
        "end_date": "2025-01-03T12:00:00",
        "duration_seconds": 14400,
        "cat_name": "STOP devējs",
        "device_name": "Press A",
        "device_location": "1 LĪNIJA ZONA",
        "comments": "",
        "is_ended": True,
    },
    {
        "id": 3,
        "start_date": "2025-01-04T08:00:00",
        "end_date": "2025-01-20T08:00:00",
        "duration_seconds": 400 * 3600,
        "cat_name": "PLĀNOTS remonts",
        "device_name": "Press B",
        "device_location": "RIPLAST HALL",
        "comments": "",
        "is_ended": True,
    },
]


def build_settings() -> Settings:
    return Settings(
        base_url="https://example.com/base",
        taskreports_url="https://example.com/reports",
        username="u",
        password="p",
        api_key="k",
    )


def test_extract_line() -> None:
    assert extract_line("RIPLAST hall") == "03. 3 LĪNIJA RIPLAST"
    assert extract_line("unknown place") == "Cits"


def test_normalize_and_filter_anomaly() -> None:
    df = normalize_downtime_rows(SAMPLE_ROWS, "lv")
    assert df.loc[0, "cat_name"] == "Nav norādīts"
    bundle = build_bundle(df, None, date(2025, 1, 1), date(2025, 1, 31), 240)
    assert bundle.excluded_anomalies == 1
    assert len(bundle.analysis) == 2


def test_kpi_calculation_matches_expected_shape() -> None:
    df = normalize_downtime_rows(SAMPLE_ROWS, "lv")
    bundle = build_bundle(df, None, date(2025, 1, 1), date(2025, 1, 31), 240)
    kpis = calculate_kpis(bundle.analysis, bundle.closed, bundle.failures)
    assert round(float(kpis["mttr"]), 2) == 3.0
    assert round(float(kpis["total_downtime_hours"]), 2) == 6.0


def test_filters_payload_uses_source_dates() -> None:
    df = normalize_downtime_rows(SAMPLE_ROWS, "lv")
    payload = build_filters_payload(df, build_settings())
    assert payload.min_date == date(2025, 1, 1)
    assert payload.max_date == date(2025, 1, 4)


def test_overview_contains_quality_alert() -> None:
    df = normalize_downtime_rows(SAMPLE_ROWS, "lv")
    bundle = build_bundle(df, None, date(2025, 1, 1), date(2025, 1, 31), 240)
    overview = build_overview_payload("lv", bundle, build_settings())
    assert overview.quality["excluded_anomalies"] == 1
    assert any(alert.id.startswith("missing") for alert in overview.alerts)
