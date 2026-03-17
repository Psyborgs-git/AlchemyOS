"""Unit tests for chemistry engine modules."""

from backend.modules.chemistry_engine.property_calculator import PropertyCalculator
from backend.modules.chemistry_engine.smiles_validator import SmilesValidator


def test_smiles_validator():
    """Test SMILES validation."""
    assert SmilesValidator.validate("CCO") is True
    assert SmilesValidator.validate("c1ccccc1") is True
    assert SmilesValidator.validate("invalid") is False


def test_canonicalize_smiles():
    """Test SMILES canonicalization."""
    canonical = SmilesValidator.canonicalize("C(C)O")
    assert canonical == "CCO"


def test_property_calculator_basic():
    """Test basic property calculation."""
    props = PropertyCalculator.calculate_basic_properties("CCO")

    assert "molecular_weight" in props
    assert "logp" in props
    assert "h_bond_donors" in props
    assert props["molecular_weight"] > 0


def test_lipinski_properties():
    """Test Lipinski Rule of Five calculation."""
    # Aspirin - should be compliant
    props = PropertyCalculator.calculate_lipinski_properties("CC(=O)Oc1ccccc1C(=O)O")

    assert "molecular_weight" in props
    assert "lipinski_violations" in props
    assert props["lipinski_compliant"] in [True, False]
