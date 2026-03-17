"""Chemistry port interface."""

from typing import Any, Protocol

from backend.core.domain.chemistry.molecule import Molecule
from backend.core.domain.chemistry.reaction import MolecularProperty


class IChemPort(Protocol):
    """Port interface for chemistry operations.

    All chemistry backends (RDKit) must implement this interface.
    """

    def validate_smiles(self, smiles: str) -> bool:
        """Validate a SMILES string.

        Args:
            smiles: SMILES string to validate

        Returns:
            True if valid, False otherwise
        """
        ...

    def smiles_to_mol(self, smiles: str) -> Any:
        """Convert SMILES to molecule object.

        Args:
            smiles: SMILES string

        Returns:
            Molecule object (implementation-specific type)
        """
        ...

    def calculate_properties(self, smiles: str) -> list[MolecularProperty]:
        """Calculate molecular properties.

        Args:
            smiles: SMILES string

        Returns:
            List of calculated properties
        """
        ...

    def get_fingerprint(self, smiles: str, fp_type: str) -> list[int]:
        """Generate molecular fingerprint.

        Args:
            smiles: SMILES string
            fp_type: Fingerprint type (morgan, maccs, etc.)

        Returns:
            Fingerprint bit vector
        """
        ...

    def smiles_to_inchi(self, smiles: str) -> tuple[str, str]:
        """Convert SMILES to InChI and InChI key.

        Args:
            smiles: SMILES string

        Returns:
            Tuple of (InChI, InChI key)
        """
        ...

    def calculate_mol_weight(self, smiles: str) -> float:
        """Calculate molecular weight.

        Args:
            smiles: SMILES string

        Returns:
            Molecular weight in g/mol
        """
        ...

    def get_molecular_formula(self, smiles: str) -> str:
        """Get molecular formula.

        Args:
            smiles: SMILES string

        Returns:
            Molecular formula
        """
        ...
