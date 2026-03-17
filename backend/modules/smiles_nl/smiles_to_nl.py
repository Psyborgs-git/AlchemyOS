"""SMILES to natural language description.

Converts SMILES strings to human-readable descriptions.
"""

from rdkit import Chem
from rdkit.Chem import Descriptors


class SmilesToNL:
    """Convert SMILES to natural language descriptions."""

    @staticmethod
    def describe(smiles: str) -> str:
        """Generate a natural language description of a molecule.

        Args:
            smiles: SMILES string

        Returns:
            Human-readable description
        """
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return "Invalid molecule"

        # Get basic properties
        formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
        mw = Descriptors.MolWt(mol)
        heavy_atoms = Descriptors.HeavyAtomCount(mol)
        rings = Descriptors.RingCount(mol)
        aromatic_rings = Descriptors.NumAromaticRings(mol)

        # Build description
        parts = [f"Molecular formula: {formula}"]
        parts.append(f"Molecular weight: {mw:.2f} g/mol")
        parts.append(f"{heavy_atoms} heavy atoms")

        if rings > 0:
            if aromatic_rings > 0:
                parts.append(f"{rings} ring(s) ({aromatic_rings} aromatic)")
            else:
                parts.append(f"{rings} ring(s)")

        # Check for functional groups
        functional_groups = SmilesToNL._identify_functional_groups(mol)
        if functional_groups:
            parts.append(f"Contains: {', '.join(functional_groups)}")

        return ". ".join(parts) + "."

    @staticmethod
    def _identify_functional_groups(mol) -> list[str]:
        """Identify common functional groups in a molecule.

        Args:
            mol: RDKit molecule object

        Returns:
            List of functional group names
        """
        groups = []

        # Define SMARTS patterns for common functional groups
        patterns = {
            "hydroxyl": "[OH]",
            "carboxylic acid": "C(=O)[OH]",
            "amine": "[NX3;H2,H1,H0]",
            "amide": "C(=O)N",
            "ester": "C(=O)O[C]",
            "ketone": "[#6][CX3](=O)[#6]",
            "aldehyde": "[CX3H1](=O)[#6]",
            "ether": "[OD2]([#6])[#6]",
            "nitro": "[$([NX3](=O)=O),$([NX3+](=O)[O-])]",
            "halogen": "[F,Cl,Br,I]",
        }

        for name, smarts in patterns.items():
            pattern = Chem.MolFromSmarts(smarts)
            if pattern and mol.HasSubstructMatch(pattern):
                groups.append(name)

        return groups

    @staticmethod
    def short_description(smiles: str) -> str:
        """Generate a short one-line description.

        Args:
            smiles: SMILES string

        Returns:
            Short description
        """
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return "Invalid molecule"

        formula = Chem.rdMolDescriptors.CalcMolFormula(mol)
        mw = Descriptors.MolWt(mol)

        return f"{formula} (MW: {mw:.1f} g/mol)"
