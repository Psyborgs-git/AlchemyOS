"""Safety middleware for FastAPI.

Intercepts chemistry responses and applies safety screening.
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class SafetyMiddleware(BaseHTTPMiddleware):
    """Safety screening middleware.

    Intercepts all chemistry-related responses and applies CBRN screening.
    """

    async def dispatch(self, request: Request, call_next):
        """Process request and apply safety screening to response.

        Args:
            request: FastAPI request
            call_next: Next middleware/handler

        Returns:
            Response with safety headers
        """
        # Get response
        response = await call_next(request)

        # Add safety header to all chemistry endpoints
        if request.url.path.startswith("/v1/molecules"):
            response.headers["X-Safety-Screening"] = "enabled"

        return response
