"""Molecule generation domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4


@dataclass
class GeneratedMolecule:
    """Generated molecule candidate entity."""

    smiles: str
    generation_run_id: UUID
    id: UUID = field(default_factory=uuid4)
    scores: dict[str, float] = field(default_factory=dict)
    rank: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate generated molecule data."""
        if not self.smiles:
            raise ValueError("SMILES cannot be empty")


@dataclass
class DesignSpec:
    """Molecule generation design specification."""

    objectives: dict[str, Any]
    constraints: dict[str, Any]
    id: UUID = field(default_factory=uuid4)
    generation_method: str = "reinvent4"
    num_molecules: int = 100
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate design spec data."""
        if not self.objectives:
            raise ValueError("Design objectives cannot be empty")
        if self.num_molecules <= 0:
            raise ValueError("Number of molecules must be positive")
        if not self.generation_method:
            raise ValueError("Generation method cannot be empty")
