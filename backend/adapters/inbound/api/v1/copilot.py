"""Copilot chat endpoint with SSE streaming."""

import json
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.core.usecases.run_copilot import RunCopilotUseCase
from backend.dependencies import get_copilot_use_case

router = APIRouter(prefix="/copilot", tags=["copilot"])


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str
    session_id: str = "default"


@router.post("/chat")
async def chat(
    request: ChatRequest,
    copilot: Annotated[RunCopilotUseCase, Depends(get_copilot_use_case)],
) -> StreamingResponse:
    """Stream copilot chat response using Server-Sent Events.

    Args:
        request: Chat request
        copilot: Copilot use case (injected)

    Returns:
        Streaming response with SSE events
    """

    async def event_stream():
        """Generate SSE event stream."""
        try:
            async for token in copilot.stream(request.message, request.session_id):
                # Send each token as a data event
                yield f"data: {json.dumps({'token': token})}\n\n"
            # Send done signal
            yield "data: [DONE]\n\n"
        except Exception as e:
            # Send error event
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
