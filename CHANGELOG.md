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
