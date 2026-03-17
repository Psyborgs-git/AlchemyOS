"""Graph database port interface."""

from typing import Any, Protocol


class IGraphPort(Protocol):
    """Port interface for graph database operations.

    All graph databases (Kuzu) must implement this interface.
    """

    async def create_node(self, label: str, properties: dict[str, Any]) -> str:
        """Create a graph node.

        Args:
            label: Node label/type
            properties: Node properties

        Returns:
            Node ID
        """
        ...

    async def create_edge(
        self, from_id: str, to_id: str, rel: str, props: dict[str, Any]
    ) -> None:
        """Create an edge between two nodes.

        Args:
            from_id: Source node ID
            to_id: Target node ID
            rel: Relationship type
            props: Edge properties
        """
        ...

    async def query(self, cypher: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        """Execute a Cypher query.

        Args:
            cypher: Cypher query string
            params: Query parameters

        Returns:
            Query results
        """
        ...

    async def get_neighbors(self, node_id: str, depth: int) -> list[dict[str, Any]]:
        """Get neighboring nodes up to a certain depth.

        Args:
            node_id: Starting node ID
            depth: Maximum traversal depth

        Returns:
            List of neighboring nodes
        """
        ...
