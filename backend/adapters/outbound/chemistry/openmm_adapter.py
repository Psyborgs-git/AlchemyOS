"""OpenMM adapter for molecular dynamics simulations.

This adapter implements molecular dynamics simulation using OpenMM.
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


class OpenMMAdapter(ISimPort):
    """OpenMM molecular dynamics simulation adapter.

    Uses OpenMM for classical molecular dynamics with force fields.
    """

    def __init__(self, data_dir: str = "./data/simulations"):
        """Initialize OpenMM adapter.

        Args:
            data_dir: Directory for storing simulation trajectories
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

    async def run_md(
        self,
        molecule_id: UUID,
        smiles: str,
        parameters: dict,
    ) -> Simulation:
        """Run molecular dynamics simulation with OpenMM.

        Args:
            molecule_id: ID of the molecule to simulate
            smiles: SMILES string of the molecule
            parameters: MD parameters including:
                - timestep: Integration timestep in fs (default: 2.0)
                - duration: Simulation duration in ps (default: 100.0)
                - temperature: Temperature in K (default: 300.0)
                - forcefield: Force field to use (default: "amber14-all.xml")
                - platform: OpenMM platform (default: "CPU")

        Returns:
            Simulation entity with results

        Raises:
            SimulationError: If simulation fails
        """
        try:
            # Import OpenMM only when needed (may not be available in all environments)
            try:
                from openmm import LangevinMiddleIntegrator, Platform, app
                from openmm.unit import kelvin, picosecond, picoseconds
            except ImportError:
                raise SimulationError(
                    "OpenMM not installed. Install with: conda install -c conda-forge openmm"
                )

            # Default parameters
            timestep = parameters.get("timestep", 2.0)  # fs
            duration = parameters.get("duration", 100.0)  # ps
            temperature = parameters.get("temperature", 300.0)  # K
            forcefield_name = parameters.get("forcefield", "amber14-all.xml")
            platform_name = parameters.get("platform", "CPU")

            # Generate 3D coordinates
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                raise SimulationError(f"Invalid SMILES: {smiles}")

            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, randomSeed=42)
            AllChem.MMFFOptimizeMolecule(mol)

            # Create simulation
            content_hash = self._compute_content_hash(
                molecule_id, SimulationType.MD, parameters
            )

            # Set up OpenMM system
            forcefield = app.ForceField(forcefield_name, "amber14/tip3p.xml")

            # Create PDB file for OpenMM
            pdb_path = self.data_dir / f"{content_hash}_input.pdb"
            Chem.MolToPDBFile(mol, str(pdb_path))

            pdb = app.PDBFile(str(pdb_path))
            system = forcefield.createSystem(
                pdb.topology,
                nonbondedMethod=app.NoCutoff,
                constraints=app.HBonds,
            )

            # Set up integrator
            integrator = LangevinMiddleIntegrator(
                temperature * kelvin,
                1 / picosecond,
                timestep / 1000 * picoseconds,  # Convert fs to ps
            )

            # Select platform
            platform = Platform.getPlatformByName(platform_name)
            simulation = app.Simulation(pdb.topology, system, integrator, platform)
            simulation.context.setPositions(pdb.positions)

            # Minimize energy
            simulation.minimizeEnergy()

            # Run MD
            num_steps = int((duration / timestep) * 1000)  # Convert ps to steps

            # Set up trajectory output
            traj_path = self.data_dir / f"{content_hash}.dcd"
            simulation.reporters.append(
                app.DCDReporter(str(traj_path), reportInterval=100)
            )

            # Run simulation
            simulation.step(num_steps)

            # Get final energy
            state = simulation.context.getState(getEnergy=True)
            final_energy = state.getPotentialEnergy().value_in_unit(
                state.getPotentialEnergy().unit
            )

            # Create simulation entity
            sim = Simulation(
                id=UUID(int=0),  # Will be set by database
                content_hash=content_hash,
                molecule_id=molecule_id,
                sim_type=SimulationType.MD,
                engine=SimulationEngine.OPENMM,
                parameters=parameters,
                status=SimulationStatus.COMPLETE,
                trajectory_path=str(traj_path),
                result_summary={
                    "final_energy_kj_mol": final_energy,
                    "num_steps": num_steps,
                    "duration_ps": duration,
                    "temperature_k": temperature,
                },
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )

            return sim

        except Exception as e:
            raise SimulationError(f"OpenMM MD simulation failed: {str(e)}") from e

    async def minimize_energy(
        self,
        molecule_id: UUID,
        smiles: str,
        parameters: dict,
    ) -> Simulation:
        """Minimize molecular energy using OpenMM.

        Args:
            molecule_id: ID of the molecule
            smiles: SMILES string of the molecule
            parameters: Minimization parameters including:
                - forcefield: Force field to use (default: "amber14-all.xml")
                - max_iterations: Maximum optimization steps (default: 1000)
                - tolerance: Energy tolerance (default: 10.0)
                - platform: OpenMM platform (default: "CPU")

        Returns:
            Simulation entity with minimized structure

        Raises:
            SimulationError: If minimization fails
        """
        try:
            # Import OpenMM
            try:
                from openmm import Platform, app
            except ImportError:
                raise SimulationError("OpenMM not installed")

            # Default parameters
            forcefield_name = parameters.get("forcefield", "amber14-all.xml")
            max_iterations = parameters.get("max_iterations", 1000)
            tolerance = parameters.get("tolerance", 10.0)
            platform_name = parameters.get("platform", "CPU")

            # Generate 3D coordinates
            mol = Chem.MolFromSmiles(smiles)
            if mol is None:
                raise SimulationError(f"Invalid SMILES: {smiles}")

            mol = Chem.AddHs(mol)
            AllChem.EmbedMolecule(mol, randomSeed=42)

            # Compute content hash
            content_hash = self._compute_content_hash(
                molecule_id, SimulationType.ENERGY_MIN, parameters
            )

            # Create PDB file
            pdb_path = self.data_dir / f"{content_hash}_input.pdb"
            Chem.MolToPDBFile(mol, str(pdb_path))

            pdb = app.PDBFile(str(pdb_path))
            forcefield = app.ForceField(forcefield_name, "amber14/tip3p.xml")
            system = forcefield.createSystem(
                pdb.topology,
                nonbondedMethod=app.NoCutoff,
            )

            # Simple integrator (not used for minimization)
            from openmm import LangevinMiddleIntegrator
            from openmm.unit import kelvin, picosecond

            integrator = LangevinMiddleIntegrator(300 * kelvin, 1 / picosecond, 0.002)

            # Select platform
            platform = Platform.getPlatformByName(platform_name)
            simulation = app.Simulation(pdb.topology, system, integrator, platform)
            simulation.context.setPositions(pdb.positions)

            # Get initial energy
            state_initial = simulation.context.getState(getEnergy=True)
            initial_energy = state_initial.getPotentialEnergy().value_in_unit(
                state_initial.getPotentialEnergy().unit
            )

            # Minimize
            simulation.minimizeEnergy(
                tolerance=tolerance,
                maxIterations=max_iterations,
            )

            # Get final energy
            state_final = simulation.context.getState(getEnergy=True)
            final_energy = state_final.getPotentialEnergy().value_in_unit(
                state_final.getPotentialEnergy().unit
            )

            # Save minimized structure
            positions = simulation.context.getState(getPositions=True).getPositions()
            output_path = self.data_dir / f"{content_hash}_minimized.pdb"
            app.PDBFile.writeFile(pdb.topology, positions, open(str(output_path), "w"))

            # Create simulation entity
            sim = Simulation(
                id=UUID(int=0),
                content_hash=content_hash,
                molecule_id=molecule_id,
                sim_type=SimulationType.ENERGY_MIN,
                engine=SimulationEngine.OPENMM,
                parameters=parameters,
                status=SimulationStatus.COMPLETE,
                trajectory_path=str(output_path),
                result_summary={
                    "initial_energy_kj_mol": initial_energy,
                    "final_energy_kj_mol": final_energy,
                    "energy_change_kj_mol": final_energy - initial_energy,
                },
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
            )

            return sim

        except Exception as e:
            raise SimulationError(f"Energy minimization failed: {str(e)}") from e

    async def get_trajectory(self, simulation_id: UUID) -> Trajectory:
        """Retrieve trajectory data.

        Note: This is a placeholder. In a full implementation, this would
        query the database for the simulation and load its trajectory.

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
