"""Molecule domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4


class SafetyStatus(str, Enum):
    """Safety screening status for molecules."""

    CLEAR = "clear"
    FLAGGED = "flagged"
    QUARANTINED = "quarantined"


class MoleculeSource(str, Enum):
    """Source of molecule data."""

    USER = "user"
    GENERATED = "generated"
    HARVESTED = "harvested"
    IMPORTED = "imported"


@dataclass
class Molecule:
    """Core molecule entity.

    Represents a chemical molecule with its structure and properties.
    All chemistry calculations are done via ports, not in this entity.
    """

    smiles: str
    inchi: str
    inchi_key: str
    formula: str
    mol_weight: float
    id: UUID = field(default_factory=uuid4)
    name: Optional[str] = None
    properties: dict[str, Any] = field(default_factory=dict)
    source: MoleculeSource = MoleculeSource.USER
    created_at: datetime = field(default_factory=datetime.utcnow)
    experiment_id: Optional[UUID] = None
    safety_status: SafetyStatus = SafetyStatus.CLEAR

    def __post_init__(self) -> None:
        """Validate molecule data after initialization."""
        if not self.smiles:
            raise ValueError("SMILES string cannot be empty")
        if not self.inchi_key:
            raise ValueError("InChI key cannot be empty")
        if self.mol_weight <= 0:
            raise ValueError("Molecular weight must be positive")
