"""Base LLM adapter with OpenAI-compatible interface."""

from typing import AsyncIterator

from openai import AsyncOpenAI

from backend.core.ports.outbound.i_llm_port import ILLMPort, Message


class BaseLLMAdapter(ILLMPort):
    """Base adapter for OpenAI-compatible LLM providers.

    This provides a unified interface for Ollama, vLLM, and OpenAI-compatible APIs.
    """

    def __init__(self, base_url: str, model: str, api_key: str = "not-needed") -> None:
        """Initialize the LLM adapter.

        Args:
            base_url: Base URL for the LLM API
            model: Model name/identifier
            api_key: API key (not needed for local runners)
        """
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = model

    async def complete(self, messages: list[Message], **kwargs) -> str:
        """Generate a completion.

        Args:
            messages: Conversation messages
            **kwargs: Additional parameters

        Returns:
            Completion text
        """
        message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]

        response = await self.client.chat.completions.create(
            model=self.model, messages=message_dicts, **kwargs
        )

        return response.choices[0].message.content or ""

    async def stream(self, messages: list[Message], **kwargs) -> AsyncIterator[str]:
        """Stream a completion.

        Args:
            messages: Conversation messages
            **kwargs: Additional parameters

        Yields:
            Completion tokens
        """
        message_dicts = [{"role": msg.role, "content": msg.content} for msg in messages]

        stream = await self.client.chat.completions.create(
            model=self.model, messages=message_dicts, stream=True, **kwargs
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def embed(self, text: str) -> list[float]:
        """Generate embedding (basic implementation).

        Args:
            text: Text to embed

        Returns:
            Embedding vector

        Note:
            This is a placeholder. Full embedding support comes in Phase 5.
        """
        # For now, return a dummy embedding
        # Real implementation will use sentence-transformers or API embeddings
        return [0.0] * 768
