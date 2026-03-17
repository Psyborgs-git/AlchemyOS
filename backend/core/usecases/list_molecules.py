"""List molecules use case."""

from backend.core.domain.chemistry.molecule import Molecule, MoleculeSource, SafetyStatus
from backend.core.ports.outbound.i_db_port import IDBPort


class ListMoleculesUseCase:
    """Use case for listing molecules."""

    def __init__(self, db_port: IDBPort) -> None:
        """Initialize use case.

        Args:
            db_port: Database port
        """
        self.db = db_port

    async def execute(self, limit: int = 100) -> list[Molecule]:
        """List molecules.

        Args:
            limit: Maximum number of molecules to return

        Returns:
            List of molecules
        """
        data_list = await self.db.list("molecules", limit=limit)

        molecules = []
        for data in data_list:
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
            molecules.append(molecule)

        return molecules
