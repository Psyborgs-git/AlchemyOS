"""Reaction domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4


@dataclass
class Reaction:
    """Chemical reaction entity.

    Represents a chemical transformation with reactants and products.
    """

    smiles: str  # Reaction SMILES format
    reactants: list[dict[str, Any]]
    products: list[dict[str, Any]]
    id: UUID = field(default_factory=uuid4)
    conditions: dict[str, Any] = field(default_factory=dict)
    yield_value: Optional[float] = None
    source: str = "user"
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate reaction data."""
        if not self.smiles:
            raise ValueError("Reaction SMILES cannot be empty")
        if not self.reactants:
            raise ValueError("Reaction must have at least one reactant")
        if not self.products:
            raise ValueError("Reaction must have at least one product")
        if self.yield_value is not None and not (0 <= self.yield_value <= 1):
            raise ValueError("Yield must be between 0 and 1")


@dataclass
class MolecularProperty:
    """Calculated or predicted molecular property."""

    molecule_id: UUID
    property_name: str
    value: float
    method: str
    id: UUID = field(default_factory=uuid4)
    unit: Optional[str] = None
    confidence: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate property data."""
        if not self.property_name:
            raise ValueError("Property name cannot be empty")
        if not self.method:
            raise ValueError("Calculation method cannot be empty")
        if self.confidence is not None and not (0 <= self.confidence <= 1):
            raise ValueError("Confidence must be between 0 and 1")


@dataclass
class Scaffold:
    """Molecular scaffold or fragment."""

    smarts: str  # SMARTS pattern
    name: str
    id: UUID = field(default_factory=uuid4)
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate scaffold data."""
        if not self.smarts:
            raise ValueError("SMARTS pattern cannot be empty")
        if not self.name:
            raise ValueError("Scaffold name cannot be empty")
