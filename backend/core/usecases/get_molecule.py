"""Get molecule use case."""

from uuid import UUID

from backend.core.domain.chemistry.molecule import Molecule, MoleculeSource, SafetyStatus
from backend.core.ports.outbound.i_db_port import IDBPort


class GetMoleculeUseCase:
    """Use case for retrieving a molecule by ID."""

    def __init__(self, db_port: IDBPort) -> None:
        """Initialize use case.

        Args:
            db_port: Database port
        """
        self.db = db_port

    async def execute(self, molecule_id: UUID) -> Molecule | None:
        """Get molecule by ID.

        Args:
            molecule_id: Molecule UUID

        Returns:
            Molecule or None if not found
        """
        data = await self.db.get("molecules", molecule_id)

        if data is None:
            return None

        # Convert to domain entity
        molecule = Molecule(
            id=data["id"],
            smiles=data["smiles"],
            inchi=data["inchi"],
            inchi_key=data["inchi_key"],
            name=data.get("name"),
            formula=data["formula"],
            mol_weight=data["mol_weight"],
            properties=data.get("properties", {}),
            source=MoleculeSource(data["source"]),
            safety_status=SafetyStatus(data["safety_status"]),
            created_at=data["created_at"],
            experiment_id=data.get("experiment_id"),
        )

        return molecule
