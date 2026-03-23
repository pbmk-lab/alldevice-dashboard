from __future__ import annotations

from typing import Any


TRANSLATIONS: dict[str, dict[str, str]] = {
    "lv": {
        "alert_missing_critical_title": "Kritiska datu kvalitāte",
        "alert_missing_critical_desc": "{value:.1f}% ierakstu ir bez cēloņa.",
        "alert_missing_warning_title": "Jāuzlabo cēloņu ievade",
        "alert_missing_warning_desc": "{value:.1f}% ierakstu ir bez cēloņa.",
        "alert_mttr_title": "Augsts MTTR",
        "alert_mttr_desc": "Vidējais remonta laiks ir {value:.2f} h.",
        "alert_anomaly_title": "Atrastas anomālas dīkstāves",
        "alert_anomaly_desc": "{count} ieraksti pārsniedz {hours} h.",
        "rec_stop_title": "Automātikas un sensoru audits",
        "rec_stop_desc": "Dominē STOP tipa cēloņi. Pārbaudīt sensorus, signālu ķēdes un automātiku.",
        "rec_missing_title": "Nostiprināt cēloņu ievadi",
        "rec_missing_desc": "Liela daļa ierakstu ir bez cēloņa. Ieviesiet obligātu cēloņa izvēli un operatīvu kontroli.",
        "rec_planned_title": "Pārplānot plānotās apkopes",
        "rec_planned_desc": "Plānotās dīkstāves rada ievērojamu slodzi. Jāpārskata apkopes logs un līniju secība.",
        "rec_default_title": "Padziļināta cēloņa analīze",
        "rec_default_desc": "Šī cēloņu grupa rada lielāko zaudējumu slogu. Nepieciešama detalizēta izpēte.",
        "priority_high": "Augsta",
        "priority_medium": "Vidēja",
        "priority_low": "Zema",
        "type_planned": "Plānots",
        "type_unplanned": "Avārija",
    },
    "en": {
        "alert_missing_critical_title": "Critical data quality issue",
        "alert_missing_critical_desc": "{value:.1f}% of records are missing a cause.",
        "alert_missing_warning_title": "Cause capture needs attention",
        "alert_missing_warning_desc": "{value:.1f}% of records are missing a cause.",
        "alert_mttr_title": "High MTTR",
        "alert_mttr_desc": "Average repair time is {value:.2f} h.",
        "alert_anomaly_title": "Anomalous downtime detected",
        "alert_anomaly_desc": "{count} records exceed {hours} h.",
        "rec_stop_title": "Audit sensors and automation",
        "rec_stop_desc": "STOP-related causes dominate. Review sensors, signal paths, and automation faults.",
        "rec_missing_title": "Tighten cause capture",
        "rec_missing_desc": "Too many records have no cause. Make cause selection mandatory and operationally reviewed.",
        "rec_planned_title": "Re-plan scheduled maintenance",
        "rec_planned_desc": "Scheduled downtime contributes a significant load. Revisit maintenance windows and line sequencing.",
        "rec_default_title": "Run deeper cause analysis",
        "rec_default_desc": "This cause group drives the largest loss burden and needs focused investigation.",
        "priority_high": "High",
        "priority_medium": "Medium",
        "priority_low": "Low",
        "type_planned": "Planned",
        "type_unplanned": "Failure",
    },
}


def t(locale: str, key: str, **kwargs: Any) -> str:
    selected_locale = locale if locale in TRANSLATIONS else "lv"
    template = TRANSLATIONS[selected_locale].get(key, key)
    return template.format(**kwargs)
