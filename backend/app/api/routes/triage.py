from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from backend.app.api.deps import get_decision_service
from backend.app.core.config import get_settings
from backend.app.domain.models import Locale, TriageResponse
from backend.app.services.decision_service import DecisionService

router = APIRouter(tags=["triage"])


@router.get("/triage/lines", response_model=TriageResponse)
async def get_triage(
    date_start: date = Query(default_factory=lambda: date.fromisoformat(get_settings().default_date_start)),
    date_end: date = Query(default_factory=lambda: date.fromisoformat(get_settings().default_date_end)),
    lines: list[str] | None = Query(default=None),
    locale: Locale = Query(default="lv"),
    service: DecisionService = Depends(get_decision_service),
) -> TriageResponse:
    return await service.get_triage(locale, date_start, date_end, lines)
