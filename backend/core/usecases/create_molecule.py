"""Create molecule use case."""

from uuid import UUID, uuid4

from backend.core.domain.chemistry.molecule import Molecule, MoleculeSource, SafetyStatus
from backend.core.ports.outbound.i_chem_port import IChemPort
from backend.core.ports.outbound.i_db_port import IDBPort
from backend.modules.safety.cbrn_screener import CBRNScreener


class CreateMoleculeUseCase:
    """Use case for creating a new molecule."""

    def __init__(self, chem_port: IChemPort, db_port: IDBPort) -> None:
        """Initialize use case.

        Args:
            chem_port: Chemistry port
            db_port: Database port
        """
        self.chem = chem_port
        self.db = db_port

    async def execute(self, smiles: str, name: str | None = None) -> Molecule | None:
        """Create a new molecule from SMILES.

        Args:
            smiles: SMILES string
            name: Optional molecule name

        Returns:
            Created molecule or None if invalid
        """
        # Validate SMILES
        if not self.chem.validate_smiles(smiles):
            return None

        # Get InChI and InChI key
        inchi, inchi_key = self.chem.smiles_to_inchi(smiles)
        if not inchi_key:
            return None

        # Calculate basic properties
        mol_weight = self.chem.calculate_mol_weight(smiles)
        formula = self.chem.get_molecular_formula(smiles)

        # Calculate detailed properties
        properties = self.chem.calculate_properties(smiles)

        # Build properties dict
        properties_dict = {prop.property_name: prop.value for prop in properties}

        # Screen for safety
        safety_status = SafetyStatus(CBRNScreener.get_safety_status(smiles))

        # Create molecule entity
        molecule = Molecule(
            id=uuid4(),
            smiles=smiles,
            inchi=inchi,
            inchi_key=inchi_key,
            name=name,
            formula=formula,
            mol_weight=mol_weight,
            properties=properties_dict,
            source=MoleculeSource.USER,
            safety_status=safety_status,
        )

        # Save to database
        molecule_data = {
            "id": molecule.id,
            "smiles": molecule.smiles,
            "inchi": molecule.inchi,
            "inchi_key": molecule.inchi_key,
            "name": molecule.name,
            "formula": molecule.formula,
            "mol_weight": molecule.mol_weight,
            "properties": molecule.properties,
            "source": molecule.source.value,
            "safety_status": molecule.safety_status.value,
            "created_at": molecule.created_at,
            "experiment_id": molecule.experiment_id,
        }

        await self.db.create("molecules", molecule_data)

        return molecule
