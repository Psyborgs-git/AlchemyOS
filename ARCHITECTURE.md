# AlchemyOS — Architecture Specification

<!-- MACHINE-PARSEABLE SPEC — LLM reads this to understand system structure -->

<!-- DO NOT restructure section headers — they are referenced by the build prompt -->

```yaml
spec_version: 1.0.0
architecture_pattern: hexagonal_ports_and_adapters
last_updated: 2025-01-01
status: blueprint
```

-----

## 1. Architectural Principles

### 1.1 Hexagonal Architecture Contract

The **Domain Core** is the center of the system. It contains:

- Domain entities (pure dataclasses / Pydantic models, no I/O)
- Use case classes (pure business logic, depend only on Port interfaces)
- Port interfaces (Python `Protocol` classes — typed contracts only)

The Domain Core **must never**:

- Import any infrastructure library (SQLAlchemy, RDKit, OpenMM, httpx, etc.)
- Perform I/O directly (no file reads, no HTTP calls, no DB queries)
- Know which adapter is wired at runtime

**Adapters** live outside the core and implement Port protocols. They are injected via dependency injection (FastAPI’s `Depends`, constructor injection in use cases).

### 1.2 Plugin Contract

All plugins implement `AlchemyPlugin` Protocol. The plugin registry auto-discovers `.py` files in `backend/plugins/`, validates them, and injects them into the agent tool registry via `watchdog` filesystem events. Hot-reload with zero restart.

### 1.3 Agent Architecture

The copilot is a **LangGraph `StateGraph`** with a shared `CopilotState` schema. The master `CopilotAgent` node routes to specialist sub-agent nodes. Sub-agents call domain use cases via ports — they never call adapters directly. The graph supports cycles (hypothesis loop).

### 1.4 Living Document Contract

The LLM build agent updates this document at the end of each phase:

1. Update `build_phase` in README.md frontmatter
1. Append phase entry to `phases_complete` array
1. Update module status table rows in README.md
1. Append `## Phase N: Name` section to CHANGELOG.md
1. Update `modules_built` list in README.md frontmatter
1. Log any issues encountered in `known_issues`

-----

## 2. Directory Structure (Canonical)

```
alchemyos/
├── README.md                            # Living doc — LLM maintains
├── ARCHITECTURE.md                      # This file — LLM references + updates
├── CHANGELOG.md                         # LLM appends after each phase
├── CONTRIBUTING.md
├── docker-compose.yml                   # Production services
├── docker-compose.dev.yml               # Dev overrides (hot-reload)
├── docker-compose.cpu.yml               # CPU-only profile
├── docker-compose.gpu.yml               # GPU profile
├── .env.example                         # All env vars documented
├── pyproject.toml                       # Python monorepo (uv/pip)
├── Makefile                             # All dev commands
│
├── backend/
│   ├── main.py                          # FastAPI app factory
│   ├── config.py                        # Pydantic Settings (reads .env)
│   ├── dependencies.py                  # DI wiring — adapters → ports
│   │
│   ├── core/                            # PURE DOMAIN — zero external imports
│   │   ├── domain/
│   │   │   ├── chemistry/
│   │   │   │   ├── molecule.py          # Molecule entity
│   │   │   │   ├── reaction.py          # Reaction entity
│   │   │   │   ├── property.py          # MolecularProperty entity
│   │   │   │   └── scaffold.py          # Scaffold / fragment entity
│   │   │   ├── simulation/
│   │   │   │   ├── simulation.py        # Simulation entity
│   │   │   │   ├── trajectory.py        # Trajectory entity
│   │   │   │   └── frame.py             # SimulationFrame entity
│   │   │   ├── hypothesis/
│   │   │   │   ├── hypothesis.py        # Hypothesis entity
│   │   │   │   ├── experiment.py        # Experiment entity
│   │   │   │   └── evidence.py          # Evidence entity
│   │   │   ├── training/
│   │   │   │   ├── training_job.py      # TrainingJob entity
│   │   │   │   ├── checkpoint.py        # ModelCheckpoint entity
│   │   │   │   └── dataset.py           # TrainingDataset entity
│   │   │   ├── generation/
│   │   │   │   ├── generated_molecule.py
│   │   │   │   └── design_spec.py       # GenerationDesignSpec entity
│   │   │   └── knowledge/
│   │   │       ├── paper.py             # Paper entity
│   │   │       ├── knowledge_node.py    # KnowledgeGraph node entity
│   │   │       └── embedding.py         # ChunkEmbedding entity
│   │   │
│   │   ├── ports/
│   │   │   ├── inbound/                 # What the domain OFFERS to callers
│   │   │   │   ├── i_run_copilot.py
│   │   │   │   ├── i_run_simulation.py
│   │   │   │   ├── i_train_model.py
│   │   │   │   ├── i_generate_molecule.py
│   │   │   │   ├── i_retrosynthesise.py
│   │   │   │   ├── i_predict_property.py
│   │   │   │   ├── i_harvest_papers.py
│   │   │   │   └── i_federate.py
│   │   │   └── outbound/                # What the domain NEEDS from infra
│   │   │       ├── i_llm_port.py
│   │   │       ├── i_db_port.py
│   │   │       ├── i_vector_port.py
│   │   │       ├── i_graph_port.py
│   │   │       ├── i_chem_port.py
│   │   │       ├── i_sim_port.py
│   │   │       ├── i_train_port.py
│   │   │       ├── i_file_port.py
│   │   │       └── i_federate_port.py
│   │   │
│   │   └── usecases/                    # Pure business logic
│   │       ├── run_hypothesis_loop.py
│   │       ├── run_simulation.py
│   │       ├── train_model.py
│   │       ├── generate_molecules.py
│   │       ├── retrosynthesis.py
│   │       ├── predict_property.py
│   │       ├── harvest_papers.py
│   │       └── evaluate_hypothesis.py
│   │
│   ├── adapters/
│   │   ├── inbound/
│   │   │   ├── api/
│   │   │   │   ├── v1/
│   │   │   │   │   ├── copilot.py       # POST /v1/copilot/chat (SSE)
│   │   │   │   │   ├── molecules.py     # CRUD + search /v1/molecules
│   │   │   │   │   ├── simulations.py   # /v1/simulations
│   │   │   │   │   ├── training.py      # /v1/training
│   │   │   │   │   ├── generation.py    # /v1/generation
│   │   │   │   │   ├── experiments.py   # /v1/experiments
│   │   │   │   │   ├── papers.py        # /v1/papers
│   │   │   │   │   └── federation.py    # /v1/federation
│   │   │   │   └── router.py            # Mounts all v1 routers
│   │   │   ├── websocket/
│   │   │   │   ├── simulation_ws.py     # Real-time simulation progress
│   │   │   │   └── training_ws.py       # Real-time training loss stream
│   │   │   └── cli/
│   │   │       ├── main.py              # Click root group
│   │   │       ├── run.py               # alchemyos run <command>
│   │   │       ├── replay.py            # alchemyos replay <exp-id>
│   │   │       └── federation.py        # alchemyos federation <command>
│   │   │
│   │   └── outbound/
│   │       ├── llm/
│   │       │   ├── base.py              # ILLMPort Protocol + BaseAdapter
│   │       │   ├── ollama_adapter.py
│   │       │   ├── vllm_adapter.py
│   │       │   └── openai_shim_adapter.py
│   │       ├── db/
│   │       │   ├── postgres_adapter.py  # SQLAlchemy 2.0 async
│   │       │   ├── pgvector_adapter.py  # Vector search (IVectorPort)
│   │       │   ├── models.py            # SQLAlchemy ORM models
│   │       │   └── migrations/          # Alembic
│   │       │       ├── env.py
│   │       │       └── versions/
│   │       ├── graph/
│   │       │   └── kuzu_adapter.py      # Kuzu embedded graph (IGraphPort)
│   │       ├── chemistry/
│   │       │   ├── rdkit_adapter.py     # IChemPort
│   │       │   ├── openmm_adapter.py    # ISimPort (MD)
│   │       │   ├── ase_adapter.py       # ISimPort (atomistic)
│   │       │   ├── mace_adapter.py      # MACE-MP neural potential
│   │       │   └── openff_adapter.py    # OpenFF force fields
│   │       ├── retrosynthesis/
│   │       │   ├── askcos_adapter.py    # ASKCOS MCTS retrosynthesis
│   │       │   └── rxnmapper_adapter.py # Reaction atom mapping
│   │       ├── generation/
│   │       │   ├── reinvent4_adapter.py
│   │       │   ├── selfies_vae_adapter.py
│   │       │   └── diffsbdd_adapter.py
│   │       ├── training/
│   │       │   ├── unsloth_adapter.py   # LoRA/QLoRA
│   │       │   ├── mace_train_adapter.py
│   │       │   └── gnn_train_adapter.py # PyTorch Geometric
│   │       ├── external/
│   │       │   ├── arxiv_client.py
│   │       │   ├── pubchem_client.py
│   │       │   ├── chembl_client.py
│   │       │   └── pubmed_client.py
│   │       └── federation/
│   │           └── libp2p_adapter.py
│   │
│   ├── agents/
│   │   ├── state.py                     # CopilotState (shared LangGraph state)
│   │   ├── copilot/
│   │   │   ├── graph.py                 # Master StateGraph definition
│   │   │   └── router.py                # Task classification → sub-agent routing
│   │   ├── retro/
│   │   │   ├── agent.py                 # RetrosynthesisAgent node
│   │   │   └── tools.py                 # LangGraph tools for retro tasks
│   │   ├── property/
│   │   │   ├── agent.py
│   │   │   └── tools.py
│   │   ├── simulation/
│   │   │   ├── agent.py                 # SimulationAgent node
│   │   │   └── tools.py
│   │   ├── training/
│   │   │   ├── agent.py
│   │   │   └── tools.py
│   │   ├── generation/
│   │   │   ├── agent.py
│   │   │   └── tools.py
│   │   ├── harvester/
│   │   │   ├── agent.py                 # PaperHarvesterAgent
│   │   │   └── tools.py
│   │   ├── hypothesis/
│   │   │   ├── agent.py                 # HypothesisAgent (cyclic loop node)
│   │   │   └── tools.py
│   │   └── sandbox/
│   │       ├── agent.py                 # CodeAgent
│   │       └── executor.py              # RestrictedPython runner
│   │
│   ├── modules/
│   │   ├── chemistry_engine/
│   │   │   ├── __init__.py
│   │   │   ├── smiles_validator.py
│   │   │   ├── property_calculator.py
│   │   │   ├── fingerprint_generator.py
│   │   │   └── scaffold_analyzer.py
│   │   ├── simulation_engine/
│   │   │   ├── __init__.py
│   │   │   ├── md_runner.py
│   │   │   ├── energy_minimizer.py
│   │   │   ├── trajectory_analyzer.py
│   │   │   └── mace_calculator.py
│   │   ├── retrosynthesis/
│   │   │   ├── __init__.py
│   │   │   ├── route_planner.py
│   │   │   ├── reaction_scorer.py
│   │   │   └── precursor_filter.py
│   │   ├── property_prediction/
│   │   │   ├── __init__.py
│   │   │   ├── gnn_predictor.py
│   │   │   ├── descriptor_predictor.py
│   │   │   └── admet_scorer.py
│   │   ├── molecule_generation/
│   │   │   ├── __init__.py
│   │   │   ├── reinvent_runner.py
│   │   │   ├── selfies_vae.py
│   │   │   ├── diffsbdd_runner.py
│   │   │   └── multi_objective_scorer.py
│   │   ├── training_hub/
│   │   │   ├── __init__.py
│   │   │   ├── lora_trainer.py
│   │   │   ├── mlip_trainer.py
│   │   │   ├── gnn_trainer.py
│   │   │   └── job_manager.py
│   │   ├── knowledge_graph/
│   │   │   ├── __init__.py
│   │   │   ├── schema.py                # Kuzu node/edge schema definitions
│   │   │   ├── queries.py               # Cypher query library
│   │   │   └── builder.py               # Graph construction from entities
│   │   ├── rag/
│   │   │   ├── __init__.py
│   │   │   ├── chunker.py               # Text + molecular chunking
│   │   │   ├── embedder.py              # ChemBERTa-2 + MiniLM embeddings
│   │   │   ├── retriever.py             # pgvector similarity search
│   │   │   └── reranker.py              # Cross-encoder reranking
│   │   ├── paper_harvester/
│   │   │   ├── __init__.py
│   │   │   ├── arxiv_harvester.py
│   │   │   ├── pubmed_harvester.py
│   │   │   ├── chembl_harvester.py
│   │   │   ├── pubchem_harvester.py
│   │   │   ├── extractor.py             # Structured data extraction via LLM
│   │   │   └── scheduler.py             # APScheduler periodic harvest
│   │   ├── safety/
│   │   │   ├── __init__.py
│   │   │   ├── cbrn_screener.py         # SMARTS-based structural alerts
│   │   │   ├── cas_checker.py           # Restricted substance CAS lookup
│   │   │   ├── toxicity_estimator.py    # LD50, Ames flags
│   │   │   └── middleware.py            # FastAPI middleware wrapping all outputs
│   │   ├── sandbox/
│   │   │   ├── __init__.py
│   │   │   ├── executor.py              # RestrictedPython + resource limits
│   │   │   └── whitelist.py             # Allowed imports + builtins
│   │   ├── experiment_tracker/
│   │   │   ├── __init__.py
│   │   │   ├── mlflow_tracker.py
│   │   │   ├── versioner.py             # Content-addressed hash IDs
│   │   │   └── replayer.py              # Deterministic experiment replay
│   │   ├── smiles_nl/
│   │   │   ├── __init__.py
│   │   │   ├── nl_to_smiles.py          # NL → SMILES via LLM + RDKit validation
│   │   │   └── smiles_to_nl.py          # SMILES → property summary in plain English
│   │   └── federation/
│   │       ├── __init__.py
│   │       ├── node.py                  # libp2p node management
│   │       ├── signer.py                # Bundle signing + verification
│   │       └── bundle.py                # Experiment bundle format
│   │
│   ├── plugins/
│   │   ├── __init__.py                  # PluginRegistry + auto-discovery
│   │   ├── plugin_base.py               # AlchemyPlugin Protocol
│   │   ├── registry.py                  # Runtime tool registry
│   │   ├── watcher.py                   # watchdog FileSystemEventHandler
│   │   └── examples/
│   │       ├── custom_scoring_plugin.py
│   │       └── custom_fingerprint_plugin.py
│   │
│   └── tests/
│       ├── unit/
│       ├── integration/
│       └── conftest.py
│
├── frontend/
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── components/
│       │   ├── copilot/
│       │   │   ├── CopilotChat.tsx      # SSE streaming chat interface
│       │   │   ├── MessageBubble.tsx
│       │   │   ├── AgentIndicator.tsx   # Shows which sub-agent is active
│       │   │   └── StreamingText.tsx
│       │   ├── molecule/
│       │   │   ├── MoleculeViewer.tsx   # 3Dmol.js 3D viewer
│       │   │   ├── SmilesEditor.tsx     # Live SMILES → 2D sketch
│       │   │   ├── PropertyCard.tsx
│       │   │   └── ScaffoldGrid.tsx
│       │   ├── simulation/
│       │   │   ├── SimulationDashboard.tsx
│       │   │   ├── TrajectoryPlayer.tsx
│       │   │   ├── EnergyPlot.tsx       # Recharts energy over time
│       │   │   └── SimParamForm.tsx
│       │   ├── training/
│       │   │   ├── TrainingDashboard.tsx
│       │   │   ├── LossPlot.tsx
│       │   │   ├── JobCard.tsx
│       │   │   └── ModelRegistry.tsx
│       │   ├── generation/
│       │   │   ├── GenerationStudio.tsx
│       │   │   ├── ObjectiveSliders.tsx # Multi-objective steering UI
│       │   │   ├── MoleculeGrid.tsx     # Generated molecule gallery
│       │   │   └── ScoringPanel.tsx
│       │   ├── experiments/
│       │   │   ├── ExperimentHistory.tsx # Git-style timeline
│       │   │   ├── ExperimentCard.tsx
│       │   │   ├── DiffViewer.tsx
│       │   │   └── ReplayButton.tsx
│       │   ├── knowledge/
│       │   │   ├── GraphExplorer.tsx    # react-force-graph
│       │   │   ├── PaperList.tsx
│       │   │   ├── SearchBar.tsx        # Semantic + keyword search
│       │   │   └── NodeDetail.tsx
│       │   ├── safety/
│       │   │   ├── SafetyBadge.tsx
│       │   │   └── ScreeningReport.tsx
│       │   └── shared/
│       │       ├── Layout.tsx
│       │       ├── Sidebar.tsx
│       │       ├── StatusBadge.tsx
│       │       └── LoadingSpinner.tsx
│       ├── pages/
│       │   ├── Lab.tsx                  # Main workspace (copilot + molecule viewer)
│       │   ├── Simulation.tsx
│       │   ├── Training.tsx
│       │   ├── Generation.tsx
│       │   ├── Library.tsx              # Molecule + paper library
│       │   ├── Experiments.tsx          # History + replay
│       │   ├── Knowledge.tsx            # Graph explorer
│       │   └── Settings.tsx
│       ├── stores/
│       │   ├── copilotStore.ts          # Zustand
│       │   ├── moleculeStore.ts
│       │   ├── simulationStore.ts
│       │   └── trainingStore.ts
│       ├── api/
│       │   ├── client.ts                # openapi-fetch typed client
│       │   └── types.ts                 # Auto-generated from FastAPI OpenAPI
│       └── workers/
│           └── smiles.worker.ts         # RDKit.js WASM in Web Worker
│
├── infra/
│   ├── postgres/
│   │   ├── init.sql                     # Extensions: pgvector, uuid-ossp
│   │   └── seed.sql
│   ├── redis/
│   │   └── redis.conf
│   └── nginx/
│       └── nginx.conf
│
└── scripts/
    ├── setup.sh
    ├── seed_data.sh
    ├── health_check.sh
    └── validate_plugins.sh
```

-----

## 3. Domain Entities Reference

### 3.1 Molecule

```python
@dataclass
class Molecule:
    id: UUID
    smiles: str
    inchi: str
    inchi_key: str
    name: Optional[str]
    formula: str
    mol_weight: float
    properties: dict[str, Any]
    source: str  # "user" | "generated" | "harvested" | "imported"
    created_at: datetime
    experiment_id: Optional[UUID]
    safety_status: SafetyStatus  # "clear" | "flagged" | "quarantined"
```

### 3.2 Simulation

```python
@dataclass
class Simulation:
    id: UUID
    content_hash: str            # Deterministic from params — used for replay
    molecule_id: UUID
    sim_type: str                # "md" | "energy_min" | "mlip" | "docking"
    engine: str                  # "openmm" | "ase" | "mace"
    parameters: dict[str, Any]
    status: str                  # "queued" | "running" | "complete" | "failed"
    trajectory_path: Optional[str]
    result_summary: Optional[dict]
    created_at: datetime
    completed_at: Optional[datetime]
    experiment_id: UUID
```

### 3.3 Hypothesis

```python
@dataclass
class Hypothesis:
    id: UUID
    statement: str               # Plain English hypothesis
    domain: str
    confidence: float            # 0.0 — 1.0
    status: str                  # "proposed" | "testing" | "supported" | "rejected" | "refined"
    evidence_ids: list[UUID]
    experiment_ids: list[UUID]
    iteration: int               # Loop count
    parent_id: Optional[UUID]    # For refined hypotheses
    created_at: datetime
    report_path: Optional[str]
```

### 3.4 TrainingJob

```python
@dataclass
class TrainingJob:
    id: UUID
    job_type: str               # "lora" | "qlora" | "mlip_mace" | "mlip_nequip" | "gnn" | "selfies_vae" | "reinvent"
    base_model: str
    dataset_id: UUID
    hyperparameters: dict
    status: str                 # "queued" | "running" | "complete" | "failed"
    checkpoint_path: Optional[str]
    metrics: dict[str, list[float]]
    hardware_profile: str       # "cpu" | "gpu" | "multi-gpu"
    created_at: datetime
    completed_at: Optional[datetime]
```

-----

## 4. Port Interface Reference

### 4.1 Outbound Ports (Domain → Infrastructure)

```python
# i_llm_port.py
class ILLMPort(Protocol):
    async def complete(self, messages: list[Message], **kwargs) -> str: ...
    async def stream(self, messages: list[Message], **kwargs) -> AsyncIterator[str]: ...
    async def embed(self, text: str) -> list[float]: ...

# i_chem_port.py
class IChemPort(Protocol):
    def validate_smiles(self, smiles: str) -> bool: ...
    def smiles_to_mol(self, smiles: str) -> Any: ...
    def calculate_properties(self, smiles: str) -> MolecularProperties: ...
    def get_fingerprint(self, smiles: str, fp_type: str) -> list[int]: ...
    def smiles_to_inchi(self, smiles: str) -> tuple[str, str]: ...

# i_sim_port.py
class ISimPort(Protocol):
    async def run_md(self, molecule: Molecule, params: SimParams) -> Simulation: ...
    async def minimize_energy(self, molecule: Molecule) -> Molecule: ...
    async def get_trajectory(self, sim_id: UUID) -> Trajectory: ...

# i_vector_port.py
class IVectorPort(Protocol):
    async def upsert(self, id: UUID, vector: list[float], payload: dict) -> None: ...
    async def search(self, query_vector: list[float], top_k: int) -> list[SearchResult]: ...
    async def delete(self, id: UUID) -> None: ...

# i_graph_port.py
class IGraphPort(Protocol):
    async def create_node(self, label: str, properties: dict) -> str: ...
    async def create_edge(self, from_id: str, to_id: str, rel: str, props: dict) -> None: ...
    async def query(self, cypher: str, params: dict) -> list[dict]: ...
    async def get_neighbors(self, node_id: str, depth: int) -> list[dict]: ...
```

-----

## 5. Agent State Schema

```python
# agents/state.py
class CopilotState(TypedDict):
    # Conversation
    messages: Annotated[list[BaseMessage], add_messages]
    user_input: str
    
    # Routing
    active_agent: str           # Current specialist agent name
    task_type: str              # Classified task type
    
    # Chemistry context
    current_molecule: Optional[dict]
    current_smiles: Optional[str]
    
    # Hypothesis loop
    current_hypothesis: Optional[dict]
    hypothesis_iteration: int
    evidence_collected: list[dict]
    
    # Execution
    tool_calls: list[dict]
    tool_results: list[dict]
    
    # Output
    final_response: Optional[str]
    generated_report: Optional[str]
    safety_flags: list[str]
    
    # Metadata
    experiment_id: Optional[str]
    session_id: str
    error: Optional[str]
```

-----

## 6. LLM Adapter Interface

All LLM runners are accessed through a unified OpenAI-compatible interface. Switching runners requires only a `.env` change.

```python
# adapters/outbound/llm/base.py
class BaseLLMAdapter(ILLMPort):
    def __init__(self, base_url: str, model: str, api_key: str = "not-needed"):
        self.client = AsyncOpenAI(base_url=base_url, api_key=api_key)
        self.model = model
    
    async def complete(self, messages, **kwargs) -> str:
        response = await self.client.chat.completions.create(
            model=self.model, messages=messages, **kwargs
        )
        return response.choices[0].message.content
    
    async def stream(self, messages, **kwargs) -> AsyncIterator[str]:
        async with self.client.chat.completions.stream(
            model=self.model, messages=messages, stream=True, **kwargs
        ) as stream:
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
```

-----

## 7. Plugin System Specification

### 7.1 AlchemyPlugin Protocol

```python
class PluginResult(BaseModel):
    success: bool
    data: dict[str, Any]
    error: Optional[str] = None
    safety_flags: list[str] = []
    metadata: dict[str, Any] = {}

class AlchemyPlugin(Protocol):
    name: str                   # Unique snake_case tool name
    description: str            # Shown to LLM — be precise and specific
    version: str                # semver
    domain: str                 # "chemistry"|"simulation"|"training"|"generation"|"knowledge"
    requires_gpu: bool          # Scheduler uses this for resource allocation
    
    def execute(self, **kwargs) -> PluginResult: ...
    def schema(self) -> dict: ...       # JSON Schema for inputs — LLM uses this
    def health_check(self) -> bool: ... # Called on load + periodically
```

### 7.2 Discovery Flow

1. `watchdog` monitors `backend/plugins/` for `*.py` file create/modify events
1. `PluginRegistry.load_file(path)` dynamically imports with `importlib.util`
1. Registry validates all `AlchemyPlugin` Protocol methods exist
1. Registry calls `health_check()` — if `False`, plugin is registered but disabled
1. Registry injects plugin as a `StructuredTool` into the LangGraph tool registry
1. Master `CopilotAgent` tool list is updated live — available in next agent invocation

-----

## 8. Safety Middleware Specification

The safety layer is a FastAPI middleware that intercepts **all** chemistry output responses:

```
Request → Router → UseCase → [Tool execution] → SafetyMiddleware → Response
```

**Screening pipeline (in order):**

1. **SMARTS structural alerts** — RDKit pattern matching against CBRN precursor library
1. **CAS number check** — against embedded restricted substance list (OPCW Schedule 1-3, DEA List I/II)
1. **Toxicity estimation** — RDKit/ML-based LD50 flag (threshold: <50 mg/kg oral rat)
1. **Ames mutagenicity** — structural alert screen
1. **Synthesis route audit** — each step in a retrosynthesis route checked independently

**Actions on flag:**

- `WARN`: Response returned with safety badge + disclaimer
- `QUARANTINE`: Response withheld, logged to safety audit table, user notified
- `BLOCK`: Response blocked, admin alert triggered

-----

## 9. Database Schema Overview

### 9.1 PostgreSQL Tables

```sql
-- Core chemistry
molecules (id, smiles, inchi, inchi_key, name, formula, mol_weight, properties jsonb, source, safety_status, created_at)
reactions (id, smiles, reactants jsonb, products jsonb, conditions jsonb, yield float, source, created_at)
properties (id, molecule_id, property_name, value float, method, created_at)

-- Simulation
simulations (id, content_hash, molecule_id, sim_type, engine, parameters jsonb, status, result_summary jsonb, created_at, completed_at)
trajectories (id, simulation_id, file_path, frame_count, duration_ps, created_at)

-- Knowledge + RAG
papers (id, title, abstract, authors jsonb, doi, arxiv_id, source, published_at, harvested_at)
chunks (id, paper_id, content text, chunk_index, embedding vector(768), created_at)

-- Hypothesis + Experiments
experiments (id, content_hash, name, description, status, created_at, completed_at)
hypotheses (id, statement, domain, confidence, status, iteration, parent_id, experiment_id, created_at)
evidence (id, hypothesis_id, type, content, source_id, support_direction, created_at)

-- Training
training_jobs (id, job_type, base_model, dataset_id, hyperparameters jsonb, status, checkpoint_path, metrics jsonb, hardware_profile, created_at, completed_at)
datasets (id, name, type, file_path, record_count, schema jsonb, created_at)

-- Safety audit
safety_events (id, action, molecule_id, flags jsonb, route, timestamp)
```

### 9.2 Kuzu Graph Schema

```
// Node types
(:Molecule {id, smiles, name})
(:Reaction {id, smarts, conditions})
(:Paper {id, doi, title})
(:Property {name, value, unit})
(:Scaffold {smarts, name})
(:Target {uniprot_id, name, organism})

// Edge types
(:Molecule)-[:HAS_PROPERTY]->(:Property)
(:Molecule)-[:CONTAINS_SCAFFOLD]->(:Scaffold)
(:Molecule)-[:BINDS_TO]->(:Target)
(:Reaction)-[:PRODUCES]->(:Molecule)
(:Reaction)-[:REQUIRES]->(:Molecule)
(:Paper)-[:DESCRIBES]->(:Molecule)
(:Paper)-[:DESCRIBES]->(:Reaction)
(:Molecule)-[:SIMILAR_TO {tanimoto: float}]->(:Molecule)
```

-----

## 10. API Contract Summary

|Method|Path                       |Description                         |Auth|
|------|---------------------------|------------------------------------|----|
|POST  |/v1/copilot/chat           |SSE streaming copilot chat          |—   |
|GET   |/v1/molecules              |List/search molecules               |—   |
|POST  |/v1/molecules              |Create molecule from SMILES         |—   |
|GET   |/v1/molecules/{id}         |Get molecule + properties           |—   |
|POST  |/v1/simulations            |Launch simulation                   |—   |
|GET   |/v1/simulations/{id}       |Get simulation status + results     |—   |
|POST  |/v1/training               |Launch training job                 |—   |
|GET   |/v1/training/{id}          |Get training job status             |—   |
|POST  |/v1/generation             |Launch molecule generation          |—   |
|GET   |/v1/generation/{id}/results|Get generated molecules             |—   |
|GET   |/v1/experiments            |List experiments (Git-style history)|—   |
|GET   |/v1/experiments/{id}       |Get experiment detail               |—   |
|POST  |/v1/experiments/{id}/replay|Replay experiment                   |—   |
|POST  |/v1/papers/harvest         |Trigger paper harvest               |—   |
|GET   |/v1/papers                 |Search papers (semantic + keyword)  |—   |
|POST  |/v1/federation/share       |Share experiment bundle             |—   |
|GET   |/v1/federation/peers       |List known peers                    |—   |
|GET   |/v1/health                 |Health check + module status        |—   |

-----

## 11. Hardware Profiles

|Profile    |RAM  |GPU             |Active Modules                                                           |Disabled                                     |
|-----------|-----|----------------|-------------------------------------------------------------------------|---------------------------------------------|
|`cpu`      |16GB |None            |chemistry_engine, retrosynthesis, rag, safety, smiles_nl, knowledge_graph|simulation_engine (GPU), diffsbdd, mace_train|
|`gpu`      |32GB |1× RTX 3090/4090|All modules                                                              |multi-gpu training                           |
|`multi-gpu`|64GB+|2+ GPUs         |All modules at full capacity                                             |—                                            |

Hardware profile is set in `.env` as `HARDWARE_PROFILE=cpu|gpu|multi-gpu`. Adapters check this at init time and load appropriate model checkpoints/backends.

-----

## 12. Build Phase Checklist

> LLM updates this table as each phase completes.

|Phase|Name                  |Status|Completed At|
|-----|----------------------|------|------------|
|0    |Foundations           |✅     |2026-03-16  |
|1    |Core Domain           |⬜     |—           |
|2    |Chemistry Engine      |⬜     |—           |
|3    |Simulation            |⬜     |—           |
|4    |Retrosynthesis        |⬜     |—           |
|5    |RAG + Knowledge       |⬜     |—           |
|6    |Training Hub          |⬜     |—           |
|7    |Generation Studio     |⬜     |—           |
|8    |Hypothesis Loop       |⬜     |—           |
|9    |Federation            |⬜     |—           |
|10   |Polish + Living README|⬜     |—           |
