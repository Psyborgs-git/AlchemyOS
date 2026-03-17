"""SMILES string validation."""

from rdkit import Chem


class SmilesValidator:
    """Validates and canonicalizes SMILES strings."""

    @staticmethod
    def validate(smiles: str) -> bool:
        """Check if SMILES string is valid.

        Args:
            smiles: SMILES string to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            return mol is not None
        except Exception:
            return False

    @staticmethod
    def canonicalize(smiles: str) -> str | None:
        """Convert SMILES to canonical form.

        Args:
            smiles: SMILES string

        Returns:
            Canonical SMILES or None if invalid
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None
            return Chem.MolToSmiles(mol, canonical=True)
        except Exception:
            return None

    @staticmethod
    def normalize(smiles: str) -> str | None:
        """Normalize SMILES (remove salts, standardize).

        Args:
            smiles: SMILES string

        Returns:
            Normalized SMILES or None if invalid
        """
        try:
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None

            # Remove salt fragments (keep largest fragment)
            from rdkit.Chem.MolStandardize import rdMolStandardize
            uncharger = rdMolStandardize.Uncharger()
            mol = uncharger.uncharge(mol)

            # Get canonical SMILES
            return Chem.MolToSmiles(mol, canonical=True)
        except Exception:
            return None
