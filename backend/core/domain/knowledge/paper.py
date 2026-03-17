"""Knowledge domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4


@dataclass
class Paper:
    """Scientific paper entity."""

    title: str
    abstract: str
    id: UUID = field(default_factory=uuid4)
    authors: list[dict[str, str]] = field(default_factory=list)
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    source: str = "user"
    published_at: Optional[datetime] = None
    harvested_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate paper data."""
        if not self.title:
            raise ValueError("Paper title cannot be empty")
        if not self.abstract:
            raise ValueError("Paper abstract cannot be empty")


@dataclass
class KnowledgeNode:
    """Knowledge graph node entity."""

    label: str
    properties: dict[str, Any]
    id: UUID = field(default_factory=uuid4)
    node_id: str = ""  # Graph database internal ID
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate knowledge node data."""
        if not self.label:
            raise ValueError("Node label cannot be empty")


@dataclass
class ChunkEmbedding:
    """Text chunk with embedding vector."""

    paper_id: UUID
    content: str
    chunk_index: int
    embedding: list[float]
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate chunk embedding data."""
        if not self.content:
            raise ValueError("Chunk content cannot be empty")
        if self.chunk_index < 0:
            raise ValueError("Chunk index must be non-negative")
        if not self.embedding:
            raise ValueError("Embedding vector cannot be empty")
