from fastapi import APIRouter

from .data_quality import router as data_quality_router
from .debug import router as debug_router
from .devices import router as devices_router
from .filters import router as filters_router
from .overview import router as overview_router
from .triage import router as triage_router
from .work_reports import router as work_reports_router

api_router = APIRouter(prefix="/api")
api_router.include_router(filters_router)
api_router.include_router(overview_router)
api_router.include_router(triage_router)
api_router.include_router(devices_router)
api_router.include_router(work_reports_router)
api_router.include_router(data_quality_router)
api_router.include_router(debug_router)
