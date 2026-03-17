"""Molecules API endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.core.domain.chemistry.molecule import Molecule
from backend.core.usecases.create_molecule import CreateMoleculeUseCase
from backend.core.usecases.get_molecule import GetMoleculeUseCase
from backend.core.usecases.list_molecules import ListMoleculesUseCase
from backend.dependencies import get_create_molecule_use_case, get_get_molecule_use_case, get_list_molecules_use_case

router = APIRouter(prefix="/molecules", tags=["molecules"])


class CreateMoleculeRequest(BaseModel):
    """Request model for creating a molecule."""

    smiles: str
    name: str | None = None


class MoleculeResponse(BaseModel):
    """Response model for molecule data."""

    id: str
    smiles: str
    inchi: str
    inchi_key: str
    name: str | None
    formula: str
    mol_weight: float
    properties: dict
    source: str
    safety_status: str
    created_at: str

    @classmethod
    def from_domain(cls, molecule: Molecule) -> "MoleculeResponse":
        """Create response from domain entity.

        Args:
            molecule: Domain molecule entity

        Returns:
            MoleculeResponse
        """
        return cls(
            id=str(molecule.id),
            smiles=molecule.smiles,
            inchi=molecule.inchi,
            inchi_key=molecule.inchi_key,
            name=molecule.name,
            formula=molecule.formula,
            mol_weight=molecule.mol_weight,
            properties=molecule.properties,
            source=molecule.source.value,
            safety_status=molecule.safety_status.value,
            created_at=molecule.created_at.isoformat(),
        )


@router.post("", response_model=MoleculeResponse, status_code=201)
async def create_molecule(
    request: CreateMoleculeRequest,
    use_case: Annotated[CreateMoleculeUseCase, Depends(get_create_molecule_use_case)],
) -> MoleculeResponse:
    """Create a new molecule from SMILES.

    Args:
        request: Create molecule request
        use_case: Create molecule use case (injected)

    Returns:
        Created molecule

    Raises:
        HTTPException: If SMILES is invalid
    """
    molecule = await use_case.execute(smiles=request.smiles, name=request.name)

    if molecule is None:
        raise HTTPException(status_code=400, detail="Invalid SMILES string")

    return MoleculeResponse.from_domain(molecule)


@router.get("/{molecule_id}", response_model=MoleculeResponse)
async def get_molecule(
    molecule_id: UUID,
    use_case: Annotated[GetMoleculeUseCase, Depends(get_get_molecule_use_case)],
) -> MoleculeResponse:
    """Get molecule by ID.

    Args:
        molecule_id: Molecule UUID
        use_case: Get molecule use case (injected)

    Returns:
        Molecule data

    Raises:
        HTTPException: If molecule not found
    """
    molecule = await use_case.execute(molecule_id)

    if molecule is None:
        raise HTTPException(status_code=404, detail="Molecule not found")

    return MoleculeResponse.from_domain(molecule)


@router.get("", response_model=list[MoleculeResponse])
async def list_molecules(
    limit: int = 100,
    use_case: Annotated[ListMoleculesUseCase, Depends(get_list_molecules_use_case)],
) -> list[MoleculeResponse]:
    """List molecules.

    Args:
        limit: Maximum number of molecules to return
        use_case: List molecules use case (injected)

    Returns:
        List of molecules
    """
    molecules = await use_case.execute(limit=limit)

    return [MoleculeResponse.from_domain(m) for m in molecules]
