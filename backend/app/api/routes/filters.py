from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from backend.app.api.deps import get_decision_service
from backend.app.domain.models import FiltersResponse, Locale
from backend.app.services.decision_service import DecisionService

router = APIRouter(tags=["filters"])


@router.get("/filters", response_model=FiltersResponse)
async def get_filters(
    locale: Locale = Query(default="lv"),
    service: DecisionService = Depends(get_decision_service),
) -> FiltersResponse:
    return await service.get_filters(locale)
