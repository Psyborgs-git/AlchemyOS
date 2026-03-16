"""Dependency injection wiring.

This module wires adapters to ports based on configuration.
All FastAPI routes use Depends() to get their dependencies from here.
"""

from backend.adapters.outbound.llm.ollama_adapter import OllamaAdapter
from backend.adapters.outbound.llm.openai_shim_adapter import OpenAIShimAdapter
from backend.adapters.outbound.llm.vllm_adapter import VLLMAdapter
from backend.config import Settings, settings
from backend.core.ports.outbound.i_llm_port import ILLMPort
from backend.core.usecases.run_copilot import RunCopilotUseCase


def get_settings() -> Settings:
    """Get application settings.

    Returns:
        Settings instance
    """
    return settings


def get_llm_adapter(settings: Settings = settings) -> ILLMPort:
    """Get LLM adapter based on configuration.

    Args:
        settings: Application settings

    Returns:
        LLM adapter instance

    Raises:
        ValueError: If LLM provider is unknown
    """
    adapters = {
        "ollama": OllamaAdapter,
        "vllm": VLLMAdapter,
        "openai_shim": OpenAIShimAdapter,
    }

    adapter_class = adapters.get(settings.llm_provider)
    if adapter_class is None:
        raise ValueError(f"Unknown LLM provider: {settings.llm_provider}")

    if settings.llm_provider == "openai_shim":
        return adapter_class(
            base_url=settings.llm_base_url,
            model=settings.llm_model,
            api_key=settings.llm_api_key,
        )
    else:
        return adapter_class(base_url=settings.llm_base_url, model=settings.llm_model)


def get_copilot_use_case(llm: ILLMPort = None) -> RunCopilotUseCase:
    """Get copilot use case with dependencies.

    Args:
        llm: LLM adapter (auto-injected)

    Returns:
        RunCopilotUseCase instance
    """
    if llm is None:
        llm = get_llm_adapter()
    return RunCopilotUseCase(llm_port=llm)
