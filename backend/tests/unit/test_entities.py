"""Unit tests for domain entities."""

from uuid import uuid4

import pytest

from backend.core.domain.chemistry.molecule import Molecule, MoleculeSource, SafetyStatus


def test_molecule_creation():
    """Test creating a valid molecule."""
    mol = Molecule(
        smiles="CCO",
        inchi="InChI=1S/C2H6O/c1-2-3/h3H,2H2,1H3",
        inchi_key="LFQSCWFLJHTTHZ-UHFFFAOYSA-N",
        formula="C2H6O",
        mol_weight=46.07,
        name="Ethanol",
    )

    assert mol.smiles == "CCO"
    assert mol.name == "Ethanol"
    assert mol.source == MoleculeSource.USER
    assert mol.safety_status == SafetyStatus.CLEAR
    assert mol.id is not None


def test_molecule_validation_empty_smiles():
    """Test that empty SMILES raises error."""
    with pytest.raises(ValueError, match="SMILES string cannot be empty"):
        Molecule(
            smiles="",
            inchi="test",
            inchi_key="test",
            formula="C",
            mol_weight=12.0,
        )


def test_molecule_validation_empty_inchi_key():
    """Test that empty InChI key raises error."""
    with pytest.raises(ValueError, match="InChI key cannot be empty"):
        Molecule(
            smiles="C",
            inchi="test",
            inchi_key="",
            formula="C",
            mol_weight=12.0,
        )


def test_molecule_validation_negative_weight():
    """Test that negative molecular weight raises error."""
    with pytest.raises(ValueError, match="Molecular weight must be positive"):
        Molecule(
            smiles="C",
            inchi="test",
            inchi_key="test",
            formula="C",
            mol_weight=-1.0,
        )


def test_molecule_with_experiment():
    """Test molecule linked to experiment."""
    experiment_id = uuid4()
    mol = Molecule(
        smiles="CCO",
        inchi="test",
        inchi_key="test",
        formula="C2H6O",
        mol_weight=46.07,
        experiment_id=experiment_id,
        source=MoleculeSource.GENERATED,
    )

    assert mol.experiment_id == experiment_id
    assert mol.source == MoleculeSource.GENERATED
