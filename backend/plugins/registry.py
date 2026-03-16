"""Plugin registry with dynamic loading."""

import importlib.util
import inspect
import sys
from pathlib import Path
from typing import Any

from backend.plugins.plugin_base import AlchemyPlugin


class PluginRegistry:
    """Registry for dynamically loaded plugins.

    Discovers and validates plugins from the plugins/ directory.
    """

    def __init__(self) -> None:
        """Initialize the plugin registry."""
        self._plugins: dict[str, Any] = {}
        self._plugin_paths: dict[str, Path] = {}

    def load_file(self, file_path: Path) -> bool:
        """Load a plugin from a Python file.

        Args:
            file_path: Path to the plugin file

        Returns:
            True if loaded successfully, False otherwise
        """
        if not file_path.exists() or file_path.suffix != ".py":
            return False

        if file_path.stem.startswith("_"):
            # Skip private files and __init__.py
            return False

        try:
            # Dynamically import the module
            spec = importlib.util.spec_from_file_location(file_path.stem, file_path)
            if spec is None or spec.loader is None:
                return False

            module = importlib.util.module_from_spec(spec)
            sys.modules[file_path.stem] = module
            spec.loader.exec_module(module)

            # Find classes that implement AlchemyPlugin
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if self._is_plugin(obj):
                    # Validate plugin
                    instance = obj()
                    if not instance.health_check():
                        print(f"Plugin {instance.name} failed health check")
                        continue

                    self._plugins[instance.name] = instance
                    self._plugin_paths[instance.name] = file_path
                    print(f"Loaded plugin: {instance.name} v{instance.version}")
                    return True

            return False

        except Exception as e:
            print(f"Failed to load plugin from {file_path}: {e}")
            return False

    def unload(self, plugin_name: str) -> bool:
        """Unload a plugin.

        Args:
            plugin_name: Name of the plugin to unload

        Returns:
            True if unloaded, False if not found
        """
        if plugin_name in self._plugins:
            del self._plugins[plugin_name]
            del self._plugin_paths[plugin_name]
            return True
        return False

    def get(self, plugin_name: str) -> Any:
        """Get a plugin by name.

        Args:
            plugin_name: Plugin name

        Returns:
            Plugin instance or None
        """
        return self._plugins.get(plugin_name)

    def list_plugins(self) -> list[dict[str, str]]:
        """List all loaded plugins.

        Returns:
            List of plugin metadata dicts
        """
        return [
            {
                "name": p.name,
                "version": p.version,
                "domain": p.domain,
                "description": p.description,
            }
            for p in self._plugins.values()
        ]

    def _is_plugin(self, obj: Any) -> bool:
        """Check if a class implements the AlchemyPlugin protocol.

        Args:
            obj: Class object to check

        Returns:
            True if it implements AlchemyPlugin
        """
        required_attrs = ["name", "description", "version", "domain", "requires_gpu"]
        required_methods = ["execute", "schema", "health_check"]

        for attr in required_attrs:
            if not hasattr(obj, attr):
                return False

        for method in required_methods:
            if not hasattr(obj, method) or not callable(getattr(obj, method)):
                return False

        return True


# Global plugin registry
plugin_registry = PluginRegistry()
