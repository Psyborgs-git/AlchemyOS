"""PostgreSQL database adapter using SQLAlchemy."""

from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from backend.adapters.outbound.db.models import Base, MoleculeModel
from backend.config import settings
from backend.core.ports.outbound.i_db_port import IDBPort


class PostgresAdapter(IDBPort):
    """PostgreSQL adapter using SQLAlchemy async.

    Implements IDBPort for database operations.
    """

    def __init__(self, database_url: str | None = None) -> None:
        """Initialize PostgreSQL adapter.

        Args:
            database_url: Database connection URL (uses settings if not provided)
        """
        self.database_url = database_url or settings.database_url
        self.engine = create_async_engine(self.database_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self) -> None:
        """Create all tables (for development/testing)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """Drop all tables (for development/testing)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def create(self, table: str, data: dict[str, Any]) -> UUID:
        """Create a new record.

        Args:
            table: Table name
            data: Record data

        Returns:
            ID of created record
        """
        async with self.async_session() as session:
            # Map table name to model
            model_class = self._get_model_class(table)

            # Create instance
            instance = model_class(**data)
            session.add(instance)
            await session.commit()
            await session.refresh(instance)

            return instance.id

    async def get(self, table: str, id: UUID) -> Optional[dict[str, Any]]:
        """Get a record by ID.

        Args:
            table: Table name
            id: Record ID

        Returns:
            Record data or None if not found
        """
        async with self.async_session() as session:
            model_class = self._get_model_class(table)

            result = await session.execute(select(model_class).where(model_class.id == id))
            instance = result.scalar_one_or_none()

            if instance is None:
                return None

            return self._model_to_dict(instance)

    async def update(self, table: str, id: UUID, data: dict[str, Any]) -> bool:
        """Update a record.

        Args:
            table: Table name
            id: Record ID
            data: Updated data

        Returns:
            True if updated, False if not found
        """
        async with self.async_session() as session:
            model_class = self._get_model_class(table)

            result = await session.execute(select(model_class).where(model_class.id == id))
            instance = result.scalar_one_or_none()

            if instance is None:
                return False

            # Update fields
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            await session.commit()
            return True

    async def delete(self, table: str, id: UUID) -> bool:
        """Delete a record.

        Args:
            table: Table name
            id: Record ID

        Returns:
            True if deleted, False if not found
        """
        async with self.async_session() as session:
            model_class = self._get_model_class(table)

            result = await session.execute(select(model_class).where(model_class.id == id))
            instance = result.scalar_one_or_none()

            if instance is None:
                return False

            await session.delete(instance)
            await session.commit()
            return True

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
        async with self.async_session() as session:
            model_class = self._get_model_class(table)

            query = select(model_class).limit(limit)

            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if hasattr(model_class, key):
                        query = query.where(getattr(model_class, key) == value)

            result = await session.execute(query)
            instances = result.scalars().all()

            return [self._model_to_dict(instance) for instance in instances]

    def _get_model_class(self, table: str) -> type:
        """Get SQLAlchemy model class for table name.

        Args:
            table: Table name

        Returns:
            Model class
        """
        models = {
            "molecules": MoleculeModel,
        }

        if table not in models:
            raise ValueError(f"Unknown table: {table}")

        return models[table]

    def _model_to_dict(self, instance: Any) -> dict[str, Any]:
        """Convert SQLAlchemy model instance to dict.

        Args:
            instance: Model instance

        Returns:
            Dictionary representation
        """
        return {
            c.name: getattr(instance, c.name) for c in instance.__table__.columns
        }
