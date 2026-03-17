"""Run copilot use case."""

from typing import AsyncIterator

from backend.core.ports.outbound.i_llm_port import ILLMPort, Message


class RunCopilotUseCase:
    """Use case for running the copilot.

    This is a stub implementation for Phase 1.
    Full LangGraph integration comes in Phase 8.
    """

    def __init__(self, llm_port: ILLMPort) -> None:
        """Initialize the use case with dependencies.

        Args:
            llm_port: LLM port for completions
        """
        self._llm = llm_port

    async def chat(self, message: str, session_id: str) -> str:
        """Send a message to the copilot.

        Args:
            message: User message
            session_id: Session ID

        Returns:
            Copilot response
        """
        messages = [Message(role="user", content=message)]
        return await self._llm.complete(messages)

    async def stream(self, message: str, session_id: str) -> AsyncIterator[str]:
        """Stream copilot response.

        Args:
            message: User message
            session_id: Session ID

        Yields:
            Response tokens
        """
        messages = [Message(role="user", content=message)]
        async for token in self._llm.stream(messages):
            yield token
