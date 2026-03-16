"""LLM port interface."""

from typing import AsyncIterator, Protocol


class Message:
    """LLM message."""

    role: str
    content: str

    def __init__(self, role: str, content: str) -> None:
        self.role = role
        self.content = content


class ILLMPort(Protocol):
    """Port interface for LLM interactions.

    All LLM providers (Ollama, vLLM, OpenAI) must implement this interface.
    """

    async def complete(self, messages: list[Message], **kwargs) -> str:
        """Generate a completion for the given messages.

        Args:
            messages: List of conversation messages
            **kwargs: Additional provider-specific parameters

        Returns:
            The completed response text
        """
        ...

    async def stream(self, messages: list[Message], **kwargs) -> AsyncIterator[str]:
        """Stream a completion token by token.

        Args:
            messages: List of conversation messages
            **kwargs: Additional provider-specific parameters

        Yields:
            Individual tokens as they are generated
        """
        ...

    async def embed(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        ...
