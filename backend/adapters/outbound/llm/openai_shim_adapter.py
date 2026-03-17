"""OpenAI-compatible shim adapter."""

from backend.adapters.outbound.llm.base import BaseLLMAdapter


class OpenAIShimAdapter(BaseLLMAdapter):
    """Adapter for any OpenAI-compatible API.

    Works with LM Studio, LocalAI, or any other OpenAI-compatible service.
    """

    def __init__(self, base_url: str, model: str, api_key: str = "not-needed") -> None:
        """Initialize OpenAI shim adapter.

        Args:
            base_url: API base URL
            model: Model identifier
            api_key: API key (if required)
        """
        super().__init__(base_url=base_url, model=model, api_key=api_key)
