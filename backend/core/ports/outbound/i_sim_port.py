"""Simulation port interface.

This port defines the contract for molecular simulation operations.
"""

from typing import Protocol
from uuid import UUID

from backend.core.domain.simulation.simulation import Simulation, Trajectory


class ISimPort(Protocol):
    """Port interface for molecular simulation operations."""

    async def run_md(
        self,
        molecule_id: UUID,
        smiles: str,
        parameters: dict,
    ) -> Simulation:
        """Run molecular dynamics simulation.

        Args:
            molecule_id: ID of the molecule to simulate
            smiles: SMILES string of the molecule
            parameters: Simulation parameters (timestep, duration, etc.)

        Returns:
            Simulation entity with results

        Raises:
            SimulationError: If simulation fails
        """
        ...

    async def minimize_energy(
        self,
        molecule_id: UUID,
        smiles: str,
        parameters: dict,
    ) -> Simulation:
        """Minimize molecular energy.

        Args:
            molecule_id: ID of the molecule
            smiles: SMILES string of the molecule
            parameters: Minimization parameters

        Returns:
            Simulation entity with minimized structure

        Raises:
            SimulationError: If minimization fails
        """
        ...

    async def get_trajectory(
        self,
        simulation_id: UUID,
    ) -> Trajectory:
        """Retrieve trajectory data for a simulation.

        Args:
            simulation_id: ID of the simulation

        Returns:
            Trajectory entity

        Raises:
            NotFoundError: If trajectory not found
        """
        ...

    async def cancel_simulation(
        self,
        simulation_id: UUID,
    ) -> bool:
        """Cancel a running simulation.

        Args:
            simulation_id: ID of the simulation to cancel

        Returns:
            True if cancelled successfully

        Raises:
            SimulationError: If cancellation fails
        """
        ...
