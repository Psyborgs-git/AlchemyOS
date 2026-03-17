"""RDKit chemistry adapter.

Implements IChemPort using RDKit for molecular operations.
"""

from typing import Any

from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, Lipinski

from backend.core.domain.chemistry.molecule import Molecule
from backend.core.domain.chemistry.reaction import MolecularProperty
from backend.core.ports.outbound.i_chem_port import IChemPort


class RDKitAdapter(IChemPort):
    """RDKit adapter for chemistry operations.

    Provides SMILES validation, property calculation, and molecular operations.
    """

    def validate_smiles(self, smiles: str) -> bool:
        """Validate a SMILES string.

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

    def smiles_to_mol(self, smiles: str) -> Any:
        """Convert SMILES to RDKit molecule object.

        Args:
            smiles: SMILES string

        Returns:
            RDKit Mol object or None if invalid
        """
        return Chem.MolFromSmiles(smiles)

    def calculate_properties(self, smiles: str) -> list[MolecularProperty]:
        """Calculate molecular properties.

        Args:
            smiles: SMILES string

        Returns:
            List of calculated properties
        """
        mol = self.smiles_to_mol(smiles)
        if mol is None:
            return []

        # Calculate common properties
        properties = []

        # Molecular weight
        mw = Descriptors.MolWt(mol)
        properties.append(
            MolecularProperty(
                molecule_id=None,  # Will be set by caller
                property_name="molecular_weight",
                value=float(mw),
                method="rdkit_descriptors",
                unit="g/mol",
                confidence=1.0,
            )
        )

        # LogP (lipophilicity)
        logp = Descriptors.MolLogP(mol)
        properties.append(
            MolecularProperty(
                molecule_id=None,
                property_name="logp",
                value=float(logp),
                method="rdkit_descriptors",
                confidence=1.0,
            )
        )

        # TPSA (topological polar surface area)
        tpsa = Descriptors.TPSA(mol)
        properties.append(
            MolecularProperty(
                molecule_id=None,
                property_name="tpsa",
                value=float(tpsa),
                method="rdkit_descriptors",
                unit="Ų",
                confidence=1.0,
            )
        )

        # Number of H-bond donors
        hbd = Descriptors.NumHDonors(mol)
        properties.append(
            MolecularProperty(
                molecule_id=None,
                property_name="h_bond_donors",
                value=float(hbd),
                method="rdkit_descriptors",
                confidence=1.0,
            )
        )

        # Number of H-bond acceptors
        hba = Descriptors.NumHAcceptors(mol)
        properties.append(
            MolecularProperty(
                molecule_id=None,
                property_name="h_bond_acceptors",
                value=float(hba),
                method="rdkit_descriptors",
                confidence=1.0,
            )
        )

        # Number of rotatable bonds
        rotatable = Descriptors.NumRotatableBonds(mol)
        properties.append(
            MolecularProperty(
                molecule_id=None,
                property_name="rotatable_bonds",
                value=float(rotatable),
                method="rdkit_descriptors",
                confidence=1.0,
            )
        )

        # QED (quantitative estimate of drug-likeness)
        try:
            from rdkit.Chem import QED
            qed = QED.qed(mol)
            properties.append(
                MolecularProperty(
                    molecule_id=None,
                    property_name="qed",
                    value=float(qed),
                    method="rdkit_qed",
                    confidence=1.0,
                )
            )
        except Exception:
            pass  # QED might not be available in all RDKit versions

        return properties

    def get_fingerprint(self, smiles: str, fp_type: str) -> list[int]:
        """Generate molecular fingerprint.

        Args:
            smiles: SMILES string
            fp_type: Fingerprint type (morgan, maccs, topological)

        Returns:
            Fingerprint bit vector as list
        """
        mol = self.smiles_to_mol(smiles)
        if mol is None:
            return []

        if fp_type == "morgan":
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)
        elif fp_type == "maccs":
            fp = AllChem.GetMACCSKeysFingerprint(mol)
        elif fp_type == "topological":
            fp = Chem.RDKFingerprint(mol)
        else:
            # Default to Morgan
            fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=2048)

        return list(fp)

    def smiles_to_inchi(self, smiles: str) -> tuple[str, str]:
        """Convert SMILES to InChI and InChI key.

        Args:
            smiles: SMILES string

        Returns:
            Tuple of (InChI, InChI key)
        """
        mol = self.smiles_to_mol(smiles)
        if mol is None:
            return "", ""

        inchi = Chem.MolToInchi(mol)
        inchi_key = Chem.MolToInchiKey(mol)

        return inchi, inchi_key

    def calculate_mol_weight(self, smiles: str) -> float:
        """Calculate molecular weight.

        Args:
            smiles: SMILES string

        Returns:
            Molecular weight in g/mol
        """
        mol = self.smiles_to_mol(smiles)
        if mol is None:
            return 0.0

        return float(Descriptors.MolWt(mol))

    def get_molecular_formula(self, smiles: str) -> str:
        """Get molecular formula.

        Args:
            smiles: SMILES string

        Returns:
            Molecular formula (e.g., "C6H12O6")
        """
        mol = self.smiles_to_mol(smiles)
        if mol is None:
            return ""

        return Chem.rdMolDescriptors.CalcMolFormula(mol)
