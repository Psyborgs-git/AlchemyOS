"""Hypothesis domain entity."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4


class HypothesisStatus(str, Enum):
    """Hypothesis lifecycle status."""

    PROPOSED = "proposed"
    TESTING = "testing"
    SUPPORTED = "supported"
    REJECTED = "rejected"
    REFINED = "refined"


@dataclass
class Hypothesis:
    """Scientific hypothesis entity.

    Represents a testable hypothesis in the research workflow.
    """

    statement: str
    domain: str
    id: UUID = field(default_factory=uuid4)
    confidence: float = 0.5
    status: HypothesisStatus = HypothesisStatus.PROPOSED
    evidence_ids: list[UUID] = field(default_factory=list)
    experiment_ids: list[UUID] = field(default_factory=list)
    iteration: int = 0
    parent_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    report_path: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate hypothesis data."""
        if not self.statement:
            raise ValueError("Hypothesis statement cannot be empty")
        if not self.domain:
            raise ValueError("Hypothesis domain cannot be empty")
        if not (0 <= self.confidence <= 1):
            raise ValueError("Confidence must be between 0 and 1")
        if self.iteration < 0:
            raise ValueError("Iteration must be non-negative")


@dataclass
class Experiment:
    """Research experiment entity."""

    name: str
    id: UUID = field(default_factory=uuid4)
    content_hash: str = ""
    description: Optional[str] = None
    status: str = "created"
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Validate experiment data."""
        if not self.name:
            raise ValueError("Experiment name cannot be empty")


@dataclass
class Evidence:
    """Scientific evidence entity."""

    hypothesis_id: UUID
    evidence_type: str
    content: str
    id: UUID = field(default_factory=uuid4)
    source_id: Optional[UUID] = None
    support_direction: str = "supporting"  # supporting, refuting, neutral
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate evidence data."""
        if not self.evidence_type:
            raise ValueError("Evidence type cannot be empty")
        if not self.content:
            raise ValueError("Evidence content cannot be empty")
        if self.support_direction not in ["supporting", "refuting", "neutral"]:
            raise ValueError("Support direction must be supporting, refuting, or neutral")
