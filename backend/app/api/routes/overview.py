from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from backend.app.api.deps import get_decision_service
from backend.app.core.config import get_settings
from backend.app.domain.models import Locale, OverviewResponse
from backend.app.services.decision_service import DecisionService

router = APIRouter(tags=["overview"])


@router.get("/overview", response_model=OverviewResponse)
async def get_overview(
    date_start: date = Query(default_factory=lambda: date.fromisoformat(get_settings().default_date_start)),
    date_end: date = Query(default_factory=lambda: date.fromisoformat(get_settings().default_date_end)),
    lines: list[str] | None = Query(default=None),
    locale: Locale = Query(default="lv"),
    service: DecisionService = Depends(get_decision_service),
) -> OverviewResponse:
    return await service.get_overview(locale, date_start, date_end, lines)
