"""Database port interface."""

from typing import Any, Optional, Protocol
from uuid import UUID


class IDBPort(Protocol):
    """Port interface for database operations.

    All database backends (PostgreSQL) must implement this interface.
    """

    async def create(self, table: str, data: dict[str, Any]) -> UUID:
        """Create a new record.

        Args:
            table: Table name
            data: Record data

        Returns:
            ID of created record
        """
        ...

    async def get(self, table: str, id: UUID) -> Optional[dict[str, Any]]:
        """Get a record by ID.

        Args:
            table: Table name
            id: Record ID

        Returns:
            Record data or None if not found
        """
        ...

    async def update(self, table: str, id: UUID, data: dict[str, Any]) -> bool:
        """Update a record.

        Args:
            table: Table name
            id: Record ID
            data: Updated data

        Returns:
            True if updated, False if not found
        """
        ...

    async def delete(self, table: str, id: UUID) -> bool:
        """Delete a record.

        Args:
            table: Table name
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        ...

    async def list(
        self, table: str, filters: Optional[dict[str, Any]] = None, limit: int = 100
    ) -> list[dict[str, Any]]:
        """List records with optional filtering.

        Args:
            table: Table name
            filters: Optional filter criteria
            limit: Maximum number of records to return

        Returns:
            List of records
        """
        ...
