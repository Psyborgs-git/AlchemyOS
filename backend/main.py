from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from watchdog.observers import Observer

from backend.adapters.inbound.api.v1.router import router as v1_router
from backend.modules.safety.middleware import SafetyMiddleware
from backend.plugins.registry import plugin_registry
from backend.plugins.watcher import PluginWatcher


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan handler.

    Initializes plugin system and starts file watcher.
    """
    # Initialize plugin system
    plugins_dir = Path(__file__).parent / "plugins"
    plugins_dir.mkdir(exist_ok=True)

    # Load existing plugins
    for plugin_file in plugins_dir.glob("*.py"):
        if not plugin_file.stem.startswith("_"):
            plugin_registry.load_file(plugin_file)

    # Start watchdog observer for hot-reload
    observer = Observer()
    event_handler = PluginWatcher(plugins_dir)
    observer.schedule(event_handler, str(plugins_dir), recursive=False)
    observer.start()

    print(f"Plugin system initialized. Watching {plugins_dir}")
    print(f"Loaded {len(plugin_registry.list_plugins())} plugins")

    yield

    # Shutdown
    observer.stop()
    observer.join()


app = FastAPI(
    title="AlchemyOS API",
    version="0.1.0",
    description="Local AI Chemistry Factory",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add safety screening middleware
app.add_middleware(SafetyMiddleware)

# Include v1 API routes
app.include_router(v1_router)


@app.get("/v1/health")
async def health() -> dict[str, str | int | list]:
    """Health check endpoint with plugin status."""
    return {
        "status": "ok",
        "version": "0.1.0",
        "phase": 2,
        "plugins": plugin_registry.list_plugins(),
        "modules": {
            "chemistry_engine": "active",
            "safety": "active",
            "smiles_nl": "active",
        },
    }
