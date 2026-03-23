from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query

from backend.app.api.deps import get_decision_service
from backend.app.core.config import get_settings
from backend.app.domain.models import DebugResponse
from backend.app.services.decision_service import DecisionService

router = APIRouter(tags=["debug"])


@router.get("/debug/upstream", response_model=DebugResponse)
async def get_debug_upstream(
    date_start: date = Query(default_factory=lambda: date.fromisoformat(get_settings().default_date_start)),
    date_end: date = Query(default_factory=lambda: date.fromisoformat(get_settings().default_date_end)),
    service: DecisionService = Depends(get_decision_service),
) -> DebugResponse:
    return await service.get_debug(date_start, date_end)
