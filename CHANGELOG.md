# CHANGELOG.md — AlchemyOS

# This file is maintained by both humans and the LLM builder.

# The LLM appends an entry after completing each build phase.

# Format: ## Phase N — [Name] — YYYY-MM-DD

-----

## Pre-Build — Architecture & Design — Initial

### Designed

- README.md: Living project documentation with frontmatter protocol
- ARCHITECTURE.md: Machine-parseable hexagonal architecture specification
- PROMPT.md: Master LLM build prompt with phase-by-phase deliverables
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
