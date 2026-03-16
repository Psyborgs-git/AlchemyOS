"""vLLM adapter."""

from backend.adapters.outbound.llm.base import BaseLLMAdapter


class VLLMAdapter(BaseLLMAdapter):
    """Adapter for vLLM inference engine.

    vLLM provides an OpenAI-compatible API.
    """

    def __init__(self, base_url: str, model: str) -> None:
        """Initialize vLLM adapter.

        Args:
            base_url: vLLM base URL (e.g., http://localhost:8080)
            model: Model name/path
        """
        super().__init__(base_url=base_url, model=model, api_key="vllm")
