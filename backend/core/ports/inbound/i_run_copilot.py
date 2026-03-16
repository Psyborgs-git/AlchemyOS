"""Copilot interaction port interface."""

from typing import AsyncIterator, Protocol


class IRunCopilot(Protocol):
    """Port interface for copilot interactions.

    This is what the API layer calls to interact with the copilot.
    """

    async def chat(self, message: str, session_id: str) -> str:
        """Send a message to the copilot and get a response.

        Args:
            message: User message
            session_id: Session identifier for conversation context

        Returns:
            Copilot response
        """
        ...

    async def stream(self, message: str, session_id: str) -> AsyncIterator[str]:
        """Stream a copilot response token by token.

        Args:
            message: User message
            session_id: Session identifier

        Yields:
            Response tokens
        """
        ...
