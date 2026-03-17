"""CBRN structural alert screening.

Screens molecules for chemical, biological, radiological, and nuclear threats.
"""

from rdkit import Chem


class CBRNScreener:
    """Screen molecules for CBRN structural alerts."""

    # SMARTS patterns for common CBRN precursors and hazardous structures
    ALERT_PATTERNS = {
        "nerve_agent_precursor": [
            "[P](=O)([F,Cl])([O,N])",  # Organophosphate nerve agent pattern
            "C(C)N(C)C=O",  # Dimethylformamide derivative
        ],
        "explosive_precursor": [
            "c1ccc([N+](=O)[O-])cc1[N+](=O)[O-]",  # Dinitrobenzene
            "[N+](=O)[O-]",  # Nitro groups (multiple)
        ],
        "toxic_halogen": [
            "c1ccccc1Cl.c1ccccc1Cl",  # Polychlorinated biphenyls
        ],
        "peroxide": [
            "[O-][O-]",  # Peroxide
            "C(OO)",  # Organic peroxide
        ],
    }

    @staticmethod
    def screen(smiles: str) -> dict[str, list[str]]:
        """Screen molecule for CBRN structural alerts.

        Args:
            smiles: SMILES string

        Returns:
            Dictionary with alert categories and matched patterns
        """
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return {}

        alerts = {}

        for category, patterns in CBRNScreener.ALERT_PATTERNS.items():
            matches = []
            for pattern_smarts in patterns:
                pattern = Chem.MolFromSmarts(pattern_smarts)
                if pattern and mol.HasSubstructMatch(pattern):
                    matches.append(pattern_smarts)

            if matches:
                alerts[category] = matches

        return alerts

    @staticmethod
    def is_flagged(smiles: str) -> bool:
        """Check if molecule has any CBRN alerts.

        Args:
            smiles: SMILES string

        Returns:
            True if alerts found, False otherwise
        """
        alerts = CBRNScreener.screen(smiles)
        return len(alerts) > 0

    @staticmethod
    def get_safety_status(smiles: str) -> str:
        """Get safety status for molecule.

        Args:
            smiles: SMILES string

        Returns:
            Safety status: "clear", "flagged", or "quarantined"
        """
        alerts = CBRNScreener.screen(smiles)

        if not alerts:
            return "clear"

        # Check severity
        high_risk_categories = ["nerve_agent_precursor", "explosive_precursor"]
        for category in high_risk_categories:
            if category in alerts:
                return "quarantined"

        return "flagged"
