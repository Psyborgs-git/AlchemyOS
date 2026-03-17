"""Plugin base protocol and result types."""

from typing import Any, Protocol

from pydantic import BaseModel


class PluginResult(BaseModel):
    """Result returned by plugin execution."""

    success: bool
    data: dict[str, Any] = {}
    error: str | None = None
    safety_flags: list[str] = []
    metadata: dict[str, Any] = {}


class AlchemyPlugin(Protocol):
    """Protocol that all AlchemyOS plugins must implement.

    Plugins are discovered automatically from the plugins/ directory
    and injected into the agent tool registry at runtime.
    """

    name: str  # Unique snake_case tool name
    description: str  # Shown to LLM — be precise and specific
    version: str  # Semver
    domain: str  # chemistry|simulation|training|generation|knowledge
    requires_gpu: bool  # Scheduler uses this for resource allocation

    def execute(self, **kwargs: Any) -> PluginResult:
        """Execute the plugin logic.

        Args:
            **kwargs: Plugin-specific parameters

        Returns:
            PluginResult with success status and data/error
        """
        ...

    def schema(self) -> dict[str, Any]:
        """Return JSON Schema for input validation.

        The LLM uses this to understand what parameters the plugin accepts.

        Returns:
            JSON Schema dict
        """
        ...

    def health_check(self) -> bool:
        """Check if the plugin is healthy and ready to execute.

        Called on load and periodically during runtime.

        Returns:
            True if healthy, False otherwise
        """
        ...
