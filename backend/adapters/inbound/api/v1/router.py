"""API v1 router aggregation."""

from fastapi import APIRouter

from backend.adapters.inbound.api.v1.copilot import router as copilot_router

# Create main v1 router
router = APIRouter(prefix="/v1")

# Include sub-routers
router.include_router(copilot_router)
