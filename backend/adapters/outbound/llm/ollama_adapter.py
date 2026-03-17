"""Ollama LLM adapter."""

from backend.adapters.outbound.llm.base import BaseLLMAdapter


class OllamaAdapter(BaseLLMAdapter):
    """Adapter for Ollama local LLM runtime.

    Ollama provides an OpenAI-compatible API at /v1.
    """

    def __init__(self, base_url: str, model: str) -> None:
        """Initialize Ollama adapter.

        Args:
            base_url: Ollama base URL (e.g., http://localhost:11434)
            model: Model name (e.g., mistral:7b-instruct)
        """
        # Ollama's OpenAI-compatible endpoint is at /v1
        if not base_url.endswith("/v1"):
            base_url = f"{base_url}/v1"

        super().__init__(base_url=base_url, model=model, api_key="ollama")
