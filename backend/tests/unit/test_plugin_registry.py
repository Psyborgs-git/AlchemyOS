"""Unit tests for plugin system."""

from pathlib import Path
from tempfile import TemporaryDirectory

from backend.plugins.plugin_base import AlchemyPlugin, PluginResult
from backend.plugins.registry import PluginRegistry


class TestPlugin:
    """Mock plugin for testing."""

    name = "test_plugin"
    description = "A test plugin"
    version = "1.0.0"
    domain = "chemistry"
    requires_gpu = False

    def execute(self, **kwargs) -> PluginResult:
        return PluginResult(success=True, data={"result": "test"})

    def schema(self) -> dict:
        return {"test_param": {"type": "string"}}

    def health_check(self) -> bool:
        return True


def test_plugin_registry_load():
    """Test loading a plugin."""
    with TemporaryDirectory() as tmpdir:
        # Create a test plugin file
        plugin_file = Path(tmpdir) / "test_plugin.py"
        plugin_file.write_text("""
from backend.plugins.plugin_base import PluginResult

class MockPlugin:
    name = "mock_plugin"
    description = "A mock plugin"
    version = "1.0.0"
    domain = "chemistry"
    requires_gpu = False

    def execute(self, **kwargs):
        return PluginResult(success=True, data={"result": "mock"})

    def schema(self):
        return {}

    def health_check(self):
        return True
""")

        # Load the plugin
        registry = PluginRegistry()
        success = registry.load_file(plugin_file)

        assert success is True
        assert "mock_plugin" in [p["name"] for p in registry.list_plugins()]


def test_plugin_registry_unload():
    """Test unloading a plugin."""
    registry = PluginRegistry()

    # Manually add a plugin
    registry._plugins["test"] = TestPlugin()

    # Unload it
    success = registry.unload("test")
    assert success is True
    assert registry.get("test") is None


def test_plugin_registry_list():
    """Test listing plugins."""
    registry = PluginRegistry()
    registry._plugins["test"] = TestPlugin()

    plugins = registry.list_plugins()

    assert len(plugins) == 1
    assert plugins[0]["name"] == "test_plugin"
    assert plugins[0]["version"] == "1.0.0"
