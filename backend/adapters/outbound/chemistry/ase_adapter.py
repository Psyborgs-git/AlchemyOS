"""ASE adapter for atomistic simulations.

This adapter provides an interface to the Atomic Simulation Environment (ASE)
for atomistic simulations and calculations.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import UUID

from rdkit import Chem
from rdkit.Chem import AllChem

from backend.core.domain.simulation.simulation import (
    Simulation,
    SimulationEngine,
    SimulationStatus,
    SimulationType,
    Trajectory,
)
from backend.core.ports.outbound.i_sim_port import ISimPort


class SimulationError(Exception):
    """Raised when simulation fails."""


class ASEAdapter(ISimPort):
    """ASE atomistic simulation adapter.

    Uses Atomic Simulation Environment for energy calculations and geometry optimization.
    """

    def __init__(self, data_dir: str = "./data/simulations"):
        """Initialize ASE adapter.

        Args:
            data_dir: Directory for storing simulation results
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _compute_content_hash(
        self,
        molecule_id: UUID,
        sim_type: SimulationType,
        parameters: dict[str, Any],
    ) -> str:
        """Compute deterministic hash for simulation reproducibility.

        Args:
            molecule_id: Molecule ID
            sim_type: Simulation type
            parameters: Simulation parameters

        Returns:
            Content hash string
        """
        content = {
            "molecule_id": str(molecule_id),
            "sim_type": sim_type.value,
            "parameters": parameters,
        }
        json_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()[:16]

    def _smiles_to_ase_atoms(self, smiles: str):
        """Convert SMILES to ASE Atoms object.

        Args:
            smiles: SMILES string

        Returns:
            ASE Atoms object

        Raises:
            SimulationError: If conversion fails
        """
        try:
            from ase import Atoms
        except ImportError:
            raise SimulationError("ASE not installed. Install with: pip install ase")

        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise SimulationError(f"Invalid SMILES: {smiles}")

        mol = Chem.AddHs(mol)
        AllChem.EmbedMolecule(mol, randomSeed=42)
        AllChem.MMFFOptimizeMolecule(mol)

        # Extract atomic numbers and positions
        conf = mol.GetConformer()
        positions = []
        symbols = []

        for atom in mol.GetAtoms():
            atomic_num = atom.GetAtomicNum()
            symbols.append(Chem.GetPeriodicTable().GetElementSymbol(atomic_num))

        for i in range(mol.GetNumAtoms()):
            pos = conf.GetAtomPosition(i)
            positions.append([pos.x, pos.y, pos.z])

        return Atoms(symbols=symbols, positions=positions)

    async def run_md(
        self,
        molecule_id: UUID,
        smiles: str,
        parameters: dict,
    ) -> Simulation:
        """Run molecular dynamics with ASE.

        Note: ASE MD is typically used with calculators like EMT or MACE.
        This is a basic implementation using Langevin dynamics.

        Args:
            molecule_id: ID of the molecule to simulate
            smiles: SMILES string of the molecule
            parameters: MD parameters including:
                - timestep: Integration timestep in fs (default: 1.0)
                - duration: Simulation duration in ps (default: 10.0)
                - temperature: Temperature in K (default: 300.0)
                - calculator: Calculator type (default: "EMT")
                - friction: Langevin friction coefficient (default: 0.002)

        Returns:
            Simulation entity with results

        Raises:
            SimulationError: If simulation fails
        """
        try:
            from ase import units
            from ase.calculators.emt import EMT
            from ase.io import Trajectory as ASETrajectory
            from ase.md.langevin import Langevin

            # Default parameters
            timestep = parameters.get("timestep", 1.0)  # fs
            duration = parameters.get("duration", 10.0)  # ps
            temperature = parameters.get("temperature", 300.0)  # K
            friction = parameters.get("friction", 0.002)

            # Convert SMILES to ASE Atoms
            atoms = self._smiles_to_ase_atoms(smiles)

            # Compute content hash
            content_hash = self._compute_content_hash(
                molecule_id, SimulationType.MD, parameters
            )

            # Set up calculator (EMT for testing, MACE for production)
            calculator_type = parameters.get("calculator", "EMT")
            if calculator_type == "EMT":
                atoms.calc = EMT()
            else:
                raise SimulationError(
                    f"Calculator {calculator_type} not supported. Use MACE adapter for ML potentials."
                )

            # Set up MD
            dyn = Langevin(
                atoms,
                timestep * units.fs,
                temperature_K=temperature,
                friction=friction,
            )

            # Set up trajectory output
            traj_path = self.data_dir / f"{content_hash}.traj"
            traj = ASETrajectory(str(traj_path), "w", atoms)
            dyn.attach(traj.write, interval=10)

            # Run MD
            num_steps = int((duration * 1000) / timestep)  # Convert ps to steps
            dyn.run(num_steps)

            # Get final energy
            final_energy = atoms.get_potential_energy()

            # Create simulation entity
            sim = Simulation(
                id=UUID(int=0),
                content_hash=content_hash,
                molecule_id=molecule_id,
                sim_type=SimulationType.MD,
                engine=SimulationEngine.ASE,
                parameters=parameters,
                status=SimulationStatus.COMPLETE,
                trajectory_path=str(traj_path),
                result_summary={
                    "final_energy_eV": float(final_energy),
                    "num_steps": num_steps,
                    "duration_ps": duration,
                    "temperature_k": temperature,
                    "calculator": calculator_type,
                },
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )

            return sim

        except ImportError as e:
            raise SimulationError(f"ASE dependencies missing: {str(e)}") from e
        except Exception as e:
            raise SimulationError(f"ASE MD simulation failed: {str(e)}") from e

    async def minimize_energy(
        self,
        molecule_id: UUID,
        smiles: str,
        parameters: dict,
    ) -> Simulation:
        """Minimize molecular energy using ASE.

        Args:
            molecule_id: ID of the molecule
            smiles: SMILES string of the molecule
            parameters: Minimization parameters including:
                - calculator: Calculator type (default: "EMT")
                - fmax: Force convergence criterion (default: 0.05 eV/Å)
                - max_steps: Maximum optimization steps (default: 200)
                - optimizer: Optimizer algorithm (default: "BFGS")

        Returns:
            Simulation entity with minimized structure

        Raises:
            SimulationError: If minimization fails
        """
        try:
            from ase.calculators.emt import EMT
            from ase.optimize import BFGS

            # Default parameters
            calculator_type = parameters.get("calculator", "EMT")
            fmax = parameters.get("fmax", 0.05)
            max_steps = parameters.get("max_steps", 200)
            optimizer_name = parameters.get("optimizer", "BFGS")

            # Convert SMILES to ASE Atoms
            atoms = self._smiles_to_ase_atoms(smiles)

            # Compute content hash
            content_hash = self._compute_content_hash(
                molecule_id, SimulationType.ENERGY_MIN, parameters
            )

            # Set up calculator
            if calculator_type == "EMT":
                atoms.calc = EMT()
            else:
                raise SimulationError(f"Calculator {calculator_type} not supported")

            # Get initial energy
            initial_energy = atoms.get_potential_energy()

            # Set up optimizer
            if optimizer_name == "BFGS":
                opt = BFGS(atoms)
            else:
                raise SimulationError(f"Optimizer {optimizer_name} not supported")

            # Run minimization
            opt.run(fmax=fmax, steps=max_steps)

            # Get final energy
            final_energy = atoms.get_potential_energy()

            # Save minimized structure
            output_path = self.data_dir / f"{content_hash}_minimized.xyz"
            from ase.io import write

            write(str(output_path), atoms)

            # Create simulation entity
            sim = Simulation(
                id=UUID(int=0),
                content_hash=content_hash,
                molecule_id=molecule_id,
                sim_type=SimulationType.ENERGY_MIN,
                engine=SimulationEngine.ASE,
                parameters=parameters,
                status=SimulationStatus.COMPLETE,
                trajectory_path=str(output_path),
                result_summary={
                    "initial_energy_eV": float(initial_energy),
                    "final_energy_eV": float(final_energy),
                    "energy_change_eV": float(final_energy - initial_energy),
                    "num_steps": opt.get_number_of_steps(),
                    "calculator": calculator_type,
                },
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )

            return sim

        except ImportError as e:
            raise SimulationError(f"ASE dependencies missing: {str(e)}") from e
        except Exception as e:
            raise SimulationError(f"Energy minimization failed: {str(e)}") from e

    async def get_trajectory(self, simulation_id: UUID) -> Trajectory:
        """Retrieve trajectory data.

        Args:
            simulation_id: ID of the simulation

        Returns:
            Trajectory entity

        Raises:
            NotImplementedError: This requires database integration
        """
        raise NotImplementedError(
            "get_trajectory requires database integration - implement in use case layer"
        )

    async def cancel_simulation(self, simulation_id: UUID) -> bool:
        """Cancel a running simulation.

        Args:
            simulation_id: ID of the simulation to cancel

        Returns:
            True if cancelled successfully

        Raises:
            NotImplementedError: Requires task queue integration
        """
        raise NotImplementedError(
            "cancel_simulation requires task queue integration (Celery)"
        )
