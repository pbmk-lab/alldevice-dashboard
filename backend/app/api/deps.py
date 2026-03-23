from __future__ import annotations

from backend.app.core.config import get_settings
from backend.app.services.decision_service import DecisionService


def get_decision_service() -> DecisionService:
    return DecisionService(get_settings())
