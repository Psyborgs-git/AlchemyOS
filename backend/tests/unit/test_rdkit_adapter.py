"""Unit tests for RDKit adapter."""

from backend.adapters.outbound.chemistry.rdkit_adapter import RDKitAdapter


def test_validate_smiles():
    """Test SMILES validation."""
    adapter = RDKitAdapter()

    # Valid SMILES
    assert adapter.validate_smiles("CCO") is True
    assert adapter.validate_smiles("c1ccccc1") is True

    # Invalid SMILES
    assert adapter.validate_smiles("") is False
    assert adapter.validate_smiles("invalid") is False


def test_calculate_mol_weight():
    """Test molecular weight calculation."""
    adapter = RDKitAdapter()

    # Ethanol (C2H6O)
    mw = adapter.calculate_mol_weight("CCO")
    assert 46.0 < mw < 47.0

    # Benzene (C6H6)
    mw = adapter.calculate_mol_weight("c1ccccc1")
    assert 78.0 < mw < 79.0


def test_smiles_to_inchi():
    """Test SMILES to InChI conversion."""
    adapter = RDKitAdapter()

    inchi, inchi_key = adapter.smiles_to_inchi("CCO")

    assert inchi.startswith("InChI=")
    assert len(inchi_key) == 27  # Standard InChI key length


def test_get_molecular_formula():
    """Test molecular formula generation."""
    adapter = RDKitAdapter()

    # Glucose
    formula = adapter.get_molecular_formula("C(C1C(C(C(C(O1)O)O)O)O)O")
    assert "C6" in formula
    assert "H12" in formula
    assert "O6" in formula
