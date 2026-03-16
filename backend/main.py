from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


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


@app.get("/v1/health")
async def health() -> dict[str, str | int]:
    return {"status": "ok", "version": "0.1.0", "phase": 0}
