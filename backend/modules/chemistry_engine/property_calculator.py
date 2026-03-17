"""Molecular property calculator."""

from rdkit import Chem
from rdkit.Chem import Descriptors, Lipinski


class PropertyCalculator:
    """Calculate molecular properties and descriptors."""

    @staticmethod
    def calculate_basic_properties(smiles: str) -> dict[str, float]:
        """Calculate basic molecular properties.

        Args:
            smiles: SMILES string

        Returns:
            Dictionary of property values
        """
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {}

        properties = {
            "molecular_weight": Descriptors.MolWt(mol),
            "logp": Descriptors.MolLogP(mol),
            "tpsa": Descriptors.TPSA(mol),
            "h_bond_donors": Descriptors.NumHDonors(mol),
            "h_bond_acceptors": Descriptors.NumHAcceptors(mol),
            "rotatable_bonds": Descriptors.NumRotatableBonds(mol),
            "aromatic_rings": Descriptors.NumAromaticRings(mol),
            "heavy_atoms": Descriptors.HeavyAtomCount(mol),
        }

        return properties

    @staticmethod
    def calculate_lipinski_properties(smiles: str) -> dict[str, float | bool]:
        """Calculate Lipinski Rule of Five properties.

        Args:
            smiles: SMILES string

        Returns:
            Dictionary with Lipinski properties and violations
        """
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {}

        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)

        # Check violations
        violations = 0
        if mw > 500:
            violations += 1
        if logp > 5:
            violations += 1
        if hbd > 5:
            violations += 1
        if hba > 10:
            violations += 1

        return {
            "molecular_weight": mw,
            "logp": logp,
            "h_bond_donors": hbd,
            "h_bond_acceptors": hba,
            "lipinski_violations": violations,
            "lipinski_compliant": violations <= 1,  # Allow 1 violation
        }

    @staticmethod
    def calculate_qed(smiles: str) -> float | None:
        """Calculate QED (Quantitative Estimate of Drug-likeness).

        Args:
            smiles: SMILES string

        Returns:
            QED score (0-1) or None if calculation fails
        """
        try:
            from rdkit.Chem import QED
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None
            return QED.qed(mol)
        except Exception:
            return None

    @staticmethod
    def calculate_sa_score(smiles: str) -> float | None:
        """Calculate synthetic accessibility score.

        Args:
            smiles: SMILES string

        Returns:
            SA score (1-10, lower is easier) or None
        """
        try:
            from rdkit.Chem import Descriptors
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                return None

            # Simplified SA score based on complexity
            # Real SA score requires additional data files
            complexity = Descriptors.BertzCT(mol)
            # Normalize to 1-10 scale (rough approximation)
            sa_score = min(10, max(1, complexity / 100))
            return sa_score
        except Exception:
            return None
