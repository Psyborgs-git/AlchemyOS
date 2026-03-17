"""Vector database port interface."""

from typing import Any, Protocol
from uuid import UUID


class SearchResult:
    """Vector search result."""

    id: UUID
    payload: dict[str, Any]
    score: float

    def __init__(self, id: UUID, payload: dict[str, Any], score: float) -> None:
        self.id = id
        self.payload = payload
        self.score = score


class IVectorPort(Protocol):
    """Port interface for vector database operations.

    All vector databases (pgvector) must implement this interface.
    """

    async def upsert(self, id: UUID, vector: list[float], payload: dict[str, Any]) -> None:
        """Insert or update a vector with metadata.

        Args:
            id: Record ID
            vector: Embedding vector
            payload: Metadata payload
        """
        ...

    async def search(self, query_vector: list[float], top_k: int) -> list[SearchResult]:
        """Search for similar vectors.

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return

        Returns:
            List of search results ordered by similarity
        """
        ...

    async def delete(self, id: UUID) -> None:
        """Delete a vector.

        Args:
            id: Record ID
        """
        ...
