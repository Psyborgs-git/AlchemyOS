# 🧪 AlchemyOS

> **An Overpowered, Composable, Local-First AI Chemistry Factory**
> Run it. Own it. Train it. Break Chemistry with it.

-----

<!-- ALCHEMYOS LIVING DOC FRONTMATTER — MACHINE READABLE — DO NOT REMOVE -->

```yaml
---
alchemyos_version: 0.1.0
build_phase: 0
phases_complete: []
phases_total: 10
modules_built: []
modules_total: 14
known_issues: []
last_updated_by: human
last_updated_at: 2025-01-01T00:00:00Z
llm_build_status: not_started
environment_validated: false
---
```

<!-- END FRONTMATTER -->

-----

## What Is AlchemyOS?

AlchemyOS is a fully local, fully composable, AI-powered chemistry research platform. It runs entirely on your hardware — from a CPU-only laptop to a multi-GPU server — with no cloud dependencies, no API keys required for core functionality, and no data leaving your machine.

It is not a wrapper around existing tools. It is an **operating system for chemistry research** — a hexagonal port/adapter architecture where every component is swappable, every model is trainable locally, every simulation is reproducible, and an AI copilot orchestrates everything via a multi-agent LangGraph system.

**What you can do with AlchemyOS:**

- Ask a question in plain English and get a synthesisable drug candidate back
- Run molecular dynamics simulations with neural network potentials (MACE-MP)
- Fine-tune chemistry LLMs on your own data with LoRA/QLoRA
- Train machine-learned interatomic potentials (MLIPs) on custom datasets
- Generate novel molecules with REINVENT4, SELFIES-VAE, and DiffSBDD
- Autonomously harvest and embed chemistry papers from ArXiv, PubMed, PubChem, ChEMBL
- Run a closed-loop hypothesis engine: propose → simulate → evaluate → refine
- Share experiment bundles with other researchers via local-first P2P federation

-----

## Module Status

|Module               |Status     |Phase|Description                        |
|---------------------|-----------|-----|-----------------------------------|
|`chemistry_engine`   |⬜ not built|2    |RDKit cheminformatics core         |
|`simulation_engine`  |⬜ not built|3    |OpenMM + ASE + MACE-MP             |
|`retrosynthesis`     |⬜ not built|4    |ASKCOS + RXNMapper                 |
|`property_prediction`|⬜ not built|2    |GNN + descriptor models            |
|`molecule_generation`|⬜ not built|7    |REINVENT4 + SELFIES-VAE + DiffSBDD |
|`training_hub`       |⬜ not built|6    |Unsloth LoRA + MACE + GNN          |
|`knowledge_graph`    |⬜ not built|5    |Kuzu embedded graph                |
|`rag`                |⬜ not built|5    |pgvector + ChemBERTa-2 RAG         |
|`paper_harvester`    |⬜ not built|5    |Agentic ArXiv/PubMed/ChEMBL scraper|
|`safety`             |⬜ not built|2    |CBRN dual-use screening            |
|`sandbox`            |⬜ not built|8    |RestrictedPython code executor     |
|`experiment_tracker` |⬜ not built|3    |MLflow local + replay system       |
|`smiles_nl`          |⬜ not built|2    |SMILES ↔ Natural language          |
|`federation`         |⬜ not built|9    |libp2p P2P experiment sharing      |


> **Status legend:** ⬜ not built · 🔨 in progress · ✅ complete · ⚠️ broken

-----

## Quick Start

### Prerequisites

- Docker + Docker Compose v2+
- Python 3.11+
- Node.js 20+
- 16GB RAM minimum (CPU), 24GB VRAM recommended for GPU paths
- [Ollama](https://ollama.ai) installed and running (or vLLM / LM Studio)

### One-Command Setup

```bash
git clone https://github.com/yourname/alchemyos
cd alchemyos
cp .env.example .env
make setup        # installs all Python deps, Node deps, runs migrations
make up           # starts Postgres, Redis, Kuzu, backend, frontend
make seed         # loads sample molecules, papers, and test data
```

Then open `http://localhost:5173` for the React UI, or `http://localhost:8000/docs` for the FastAPI Swagger UI.

### LLM Configuration

AlchemyOS uses a unified OpenAI-compatible adapter. Configure your runner in `.env`:

```env
# Ollama (default)
LLM_PROVIDER=ollama
LLM_BASE_URL=http://localhost:11434
LLM_MODEL=mistral:7b-instruct

# vLLM
LLM_PROVIDER=vllm
LLM_BASE_URL=http://localhost:8080
LLM_MODEL=mistralai/Mistral-7B-Instruct-v0.3

# LM Studio / any OpenAI-compatible
LLM_PROVIDER=openai_shim
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=local-model
LLM_API_KEY=not-needed
```

### Hardware Profiles

```bash
make up PROFILE=cpu          # CPU only (16GB RAM), uses lighter models
make up PROFILE=gpu          # Single GPU (RTX 3090/4090), full feature set
make up PROFILE=multi-gpu    # Multi-GPU server, all modules at full capacity
```

-----

## Architecture Overview

AlchemyOS follows **Hexagonal (Ports & Adapters)** architecture strictly. The domain core is pure Python with zero I/O dependencies. All infrastructure (databases, LLMs, chemistry libraries, external APIs) is accessed through typed Port interfaces with swappable Adapters.

```
┌─────────────────────────────────────────────────────────────┐
│                    DRIVING ADAPTERS                         │
│   React UI  │  FastAPI REST  │  WebSocket  │  CLI           │
└──────────────────────────┬──────────────────────────────────┘
                           │ Inbound Ports
┌──────────────────────────▼──────────────────────────────────┐
│                      DOMAIN CORE                            │
│   Entities │ Use Cases │ Copilot Orchestrator (LangGraph)   │
│                 8 Specialist Sub-Agents                     │
└──────────────────────────┬──────────────────────────────────┘
                           │ Outbound Ports
┌──────────────────────────▼──────────────────────────────────┐
│                    DRIVEN ADAPTERS                          │
│  LLM │ Postgres+pgvector │ Kuzu │ Redis │ RDKit │ OpenMM   │
│  ASE │ MACE-MP │ ASKCOS │ REINVENT4 │ Unsloth │ libp2p    │
└─────────────────────────────────────────────────────────────┘
```

Full architectural detail: see [ARCHITECTURE.md](./ARCHITECTURE.md)

-----

## The AI Copilot

The copilot is not a chatbot. It is a **multi-agent orchestration system** built on LangGraph with a stateful directed graph. A master `CopilotAgent` routes tasks to 8 specialist sub-agents:

|Agent            |Responsibility                                            |
|-----------------|----------------------------------------------------------|
|`RetroAgent`     |Retrosynthesis, reaction pathway planning                 |
|`PropertyAgent`  |Molecular property prediction and scoring                 |
|`SimAgent`       |MD simulation setup, execution, analysis                  |
|`TrainAgent`     |Model training job creation and monitoring                |
|`GenAgent`       |Molecule generation with multi-objective steering         |
|`HarvesterAgent` |Autonomous paper scraping and knowledge base updates      |
|`HypothesisAgent`|Closed-loop hypothesis formulation, evaluation, refinement|
|`CodeAgent`      |Python code generation and sandboxed execution            |

The copilot can:

- Explain simulation results in plain language
- Suggest next experiments based on current evidence
- Write and execute Python code in a sandboxed environment
- Evaluate hypotheses against embedded literature
- Harvest and embed relevant papers autonomously
- Create and launch AI training pipelines
- Generate hypothesis reports as PDF/Markdown documents

-----

## Plugin System

Drop any `.py` file into `backend/plugins/` and it becomes a tool available to the AI copilot immediately — no restart required. The watchdog daemon detects new files, validates them against the `AlchemyPlugin` protocol, and injects them into the agent tool registry.

```python
# backend/plugins/my_custom_scorer.py
from plugins.plugin_base import AlchemyPlugin, PluginResult

class MyCustomScorer(AlchemyPlugin):
    name = "custom_qed_scorer"
    description = "Scores molecules using my custom QED variant"
    version = "0.1.0"
    domain = "chemistry"

    def execute(self, smiles: str, **kwargs) -> PluginResult:
        # your logic here
        return PluginResult(success=True, data={"score": 0.87})

    def schema(self) -> dict:
        return {"smiles": {"type": "string", "required": True}}

    def health_check(self) -> bool:
        return True
```

Save the file. The copilot can use `custom_qed_scorer` in its next message.

-----

## Training Hub

AlchemyOS can train the following model types locally:

|Type                 |Framework             |Use Case                                       |
|---------------------|----------------------|-----------------------------------------------|
|Chemistry LLM (LoRA) |Unsloth + PEFT        |Fine-tune Mistral/LLaMA on chemistry literature|
|Chemistry LLM (QLoRA)|Unsloth + BitsAndBytes|Fine-tune on 4-bit quantized base              |
|MLIP (MACE)          |MACE + e3nn           |Train neural interatomic potentials on DFT data|
|MLIP (NequIP)        |NequIP + PyTorch      |Equivariant GNN for molecular dynamics         |
|Property Prediction  |PyTorch Geometric     |GNN for ADMET, solubility, toxicity            |
|Molecule Generator   |SELFIES-VAE           |Variational autoencoder for SMILES/SELFIES     |
|Custom Generator     |REINVENT4 RL          |Reinforcement learning over chemical space     |

Training jobs are launched via the copilot (`"train a property prediction model on this dataset"`), the REST API, or the CLI.

-----

## Safety

All molecule, reaction, and synthesis outputs pass through the CBRN safety screening middleware before being returned to the user. This is not optional and cannot be disabled via the API. It checks:

- Known CBRN precursor structural alerts (RDKit SMARTS-based)
- CAS number matching against restricted substance lists
- Toxicity threshold flags (LD50 estimation, Ames mutagenicity)
- Dual-use pattern detection on synthesis routes

Flagged results are quarantined, logged, and the user is informed. Override requires explicit admin configuration.

-----

## Experiment Versioning

Every simulation, training job, and generation run is assigned a content-addressed hash ID. Experiments are fully reproducible:

```bash
alchemyos replay exp_7f3a9c2b    # re-run exact simulation with same parameters
alchemyos diff exp_7f3a9c2b exp_9b1f4e7a   # compare two experiments
alchemyos export exp_7f3a9c2b --format bundle  # export for federation
```

-----

## Federation

Share experiments with collaborators without a central server:

```bash
alchemyos federation start           # start P2P node
alchemyos federation share exp_7f3a9c2b --peer <peer-id>
alchemyos federation import bundle.alch
```

All shared bundles are cryptographically signed. Only experiment configs, model weights (opt-in), and result metadata are shared — never raw user data.

-----

## Development

```bash
make dev              # hot-reload backend + frontend
make test             # full test suite (pytest + vitest)
make test-integration # testcontainers integration tests
make lint             # ruff + mypy + eslint
make migrate          # run Alembic migrations
make plugin-check     # validate all plugins in /plugins dir
```

-----

## Changelog

> This section is maintained by the LLM build agent. Each completed phase appends an entry.

*(No phases complete yet — build not started)*

-----

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md). All chemistry tool adapters, new plugins, and training integrations are welcome. The plugin system is the primary extension point — you do not need to modify core domain code to add new capabilities.

-----

## License

MIT. Use it for good science.
