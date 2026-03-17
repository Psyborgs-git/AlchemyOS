"""Simulation domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4


class SimulationType(str, Enum):
    """Types of molecular simulations."""

    MD = "md"
    ENERGY_MIN = "energy_min"
    MLIP = "mlip"
    DOCKING = "docking"


class SimulationEngine(str, Enum):
    """Simulation engine backends."""

    OPENMM = "openmm"
    ASE = "ase"
    MACE = "mace"


class SimulationStatus(str, Enum):
    """Simulation execution status."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class Simulation:
    """Molecular simulation entity.

    Represents a simulation run with its configuration and results.
    """

    molecule_id: UUID
    sim_type: SimulationType
    engine: SimulationEngine
    parameters: dict[str, Any]
    id: UUID = field(default_factory=uuid4)
    content_hash: str = ""  # Deterministic hash for replay
    status: SimulationStatus = SimulationStatus.QUEUED
    trajectory_path: Optional[str] = None
    result_summary: Optional[dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    experiment_id: Optional[UUID] = None

    def __post_init__(self) -> None:
        """Validate simulation data."""
        if not self.parameters:
            raise ValueError("Simulation parameters cannot be empty")


@dataclass
class Trajectory:
    """Molecular dynamics trajectory."""

    simulation_id: UUID
    file_path: str
    frame_count: int
    id: UUID = field(default_factory=uuid4)
    duration_ps: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate trajectory data."""
        if not self.file_path:
            raise ValueError("Trajectory file path cannot be empty")
        if self.frame_count <= 0:
            raise ValueError("Frame count must be positive")
