"""API v1 router aggregation."""

from fastapi import APIRouter

from backend.adapters.inbound.api.v1.copilot import router as copilot_router
from backend.adapters.inbound.api.v1.molecules import router as molecules_router

# Create main v1 router
router = APIRouter(prefix="/v1")

# Include sub-routers
router.include_router(copilot_router)
router.include_router(molecules_router)
