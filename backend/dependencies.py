"""Dependency injection wiring.

This module wires adapters to ports based on configuration.
All FastAPI routes use Depends() to get their dependencies from here.
"""

from backend.adapters.outbound.chemistry.rdkit_adapter import RDKitAdapter
from backend.adapters.outbound.db.postgres_adapter import PostgresAdapter
from backend.adapters.outbound.llm.ollama_adapter import OllamaAdapter
from backend.adapters.outbound.llm.openai_shim_adapter import OpenAIShimAdapter
from backend.adapters.outbound.llm.vllm_adapter import VLLMAdapter
from backend.config import Settings, settings
from backend.core.ports.outbound.i_chem_port import IChemPort
from backend.core.ports.outbound.i_db_port import IDBPort
from backend.core.ports.outbound.i_llm_port import ILLMPort
from backend.core.usecases.create_molecule import CreateMoleculeUseCase
from backend.core.usecases.get_molecule import GetMoleculeUseCase
from backend.core.usecases.list_molecules import ListMoleculesUseCase
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


def get_chem_adapter() -> IChemPort:
    """Get chemistry adapter.

    Returns:
        RDKit chemistry adapter
    """
    return RDKitAdapter()


def get_db_adapter() -> IDBPort:
    """Get database adapter.

    Returns:
        PostgreSQL database adapter
    """
    return PostgresAdapter()


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


def get_create_molecule_use_case(
    chem: IChemPort = None, db: IDBPort = None
) -> CreateMoleculeUseCase:
    """Get create molecule use case.

    Args:
        chem: Chemistry adapter
        db: Database adapter

    Returns:
        CreateMoleculeUseCase instance
    """
    if chem is None:
        chem = get_chem_adapter()
    if db is None:
        db = get_db_adapter()
    return CreateMoleculeUseCase(chem_port=chem, db_port=db)


def get_get_molecule_use_case(db: IDBPort = None) -> GetMoleculeUseCase:
    """Get get molecule use case.

    Args:
        db: Database adapter

    Returns:
        GetMoleculeUseCase instance
    """
    if db is None:
        db = get_db_adapter()
    return GetMoleculeUseCase(db_port=db)


def get_list_molecules_use_case(db: IDBPort = None) -> ListMoleculesUseCase:
    """Get list molecules use case.

    Args:
        db: Database adapter

    Returns:
        ListMoleculesUseCase instance
    """
    if db is None:
        db = get_db_adapter()
    return ListMoleculesUseCase(db_port=db)
