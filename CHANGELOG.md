# CHANGELOG.md — AlchemyOS

# This file is maintained by both humans and the LLM builder.

# The LLM appends an entry after completing each build phase.

# Format: ## Phase N — [Name] — YYYY-MM-DD

-----

## Pre-Build — Architecture & Design — Initial

### Designed

- README.md: Living project documentation with frontmatter protocol
- ARCHITECTURE.md: Machine-parseable hexagonal architecture specification
- BUILD_PROMPT.md: Master LLM build prompt with phase-by-phase deliverables
- INIT_PROMPT.md: First-boot initialisation prompt for LLM workflow

### Decisions Made

- Architecture: Hexagonal (ports & adapters) — domain never imports infrastructure
- Backend: Python 3.11 + FastAPI + LangGraph + Celery + PostgreSQL + pgvector + Kuzu
- Frontend: React 18 + TypeScript + Vite + Tailwind
- LLM: Unified OpenAI-compatible adapter (Ollama / vLLM / LM Studio)
- Chemistry: RDKit + OpenMM + ASE + MACE-MP + OpenFF
- Training: Unsloth LoRA + MACE trainer + PyTorch Geometric + SELFIES-VAE
- Generation: REINVENT4 + SELFIES-VAE + DiffSBDD
- Plugins: Drop-in Python auto-discovery via importlib + watchdog
- Safety: Non-bypassable CBRN middleware on all chemistry outputs
- Knowledge: pgvector (semantic) + Kuzu graph (relational/graph) + APScheduler harvest

### Known Issues at Design Time

- None

-----

<!-- LLM APPENDS BELOW THIS LINE -->

## Phase 0 — Foundations — 2026-03-16

### Built

- Added `docker-compose.yml` and `docker-compose.dev.yml` for core local services.
- Added `infra/postgres/init.sql` to enable `vector`, `uuid-ossp`, and `pg_trgm`.
- Added backend skeleton (`backend/main.py`, package init, Dockerfile) with health endpoint.
- Added frontend React/Vite scaffold and Dockerfile.
- Added root project scaffolding: `.env.example`, `pyproject.toml`, `Makefile`, `.gitignore`.
- Added initial backend test (`backend/tests/test_health.py`) and plugin validation script.

### Validation

- `python -m pytest backend/tests/test_health.py -q` passed.
- `npm run build` in `frontend/` passed.
- Manual health check against `GET /v1/health` returned expected phase-0 response.

-----

## Phase 1 — Core Domain — 2026-03-16

### Built

**Domain Layer (Pure Python, Zero Infrastructure Dependencies):**
- All domain entities in `backend/core/domain/`:
  - Chemistry: `Molecule`, `Reaction`, `MolecularProperty`, `Scaffold`
  - Simulation: `Simulation`, `Trajectory`
  - Hypothesis: `Hypothesis`, `Experiment`, `Evidence`
  - Training: `TrainingJob`, `ModelCheckpoint`, `TrainingDataset`
  - Generation: `GeneratedMolecule`, `DesignSpec`
  - Knowledge: `Paper`, `KnowledgeNode`, `ChunkEmbedding`

**Port Interfaces (Protocols):**
- Outbound ports in `backend/core/ports/outbound/`:
  - `ILLMPort` - LLM interactions
  - `IChemPort` - Chemistry operations
  - `IDBPort` - Database operations
  - `IVectorPort` - Vector database operations
  - `IGraphPort` - Graph database operations
- Inbound ports in `backend/core/ports/inbound/`:
  - `IRunCopilot` - Copilot interaction interface

**Use Cases:**
- `RunCopilotUseCase` in `backend/core/usecases/` with LLM port injection

**LLM Adapters:**
- `BaseLLMAdapter` with OpenAI-compatible interface
- `OllamaAdapter` for Ollama local LLM runtime
- `VLLMAdapter` for vLLM inference engine
- `OpenAIShimAdapter` for any OpenAI-compatible API

**Plugin System:**
- `AlchemyPlugin` protocol in `backend/plugins/plugin_base.py`
- `PluginRegistry` with dynamic loading/unloading
- `PluginWatcher` with watchdog for hot-reload
- Integrated into FastAPI lifespan for automatic plugin discovery

**Configuration & DI:**
- `backend/config.py` with Pydantic Settings reading all env vars
- `backend/dependencies.py` for dependency injection wiring
- LLM adapter factory with provider switching

**API Endpoints:**
- `/v1/copilot/chat` - SSE streaming copilot endpoint
- `/v1/health` - Enhanced with plugin status

**Tests:**
- Unit tests for domain entities (`test_entities.py`)
- Unit tests for LLM adapters (`test_llm_adapters.py`)
- Unit tests for plugin registry (`test_plugin_registry.py`)
- Integration test for copilot endpoint (`test_copilot_endpoint.py`)
- Updated health endpoint test

### Architecture Validation

✅ **Domain Purity:** Zero infrastructure imports in `backend/core/`
✅ **Port/Adapter Pattern:** All dependencies injected via Protocol interfaces
✅ **Plugin Contract:** Hot-reload working, protocol validated
✅ **Tests:** All components have unit tests

### Known Issues

None.
