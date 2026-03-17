"""Filesystem watcher for hot-reload of plugins."""

from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler

from backend.plugins.registry import plugin_registry


class PluginWatcher(FileSystemEventHandler):
    """Watches the plugins directory for changes and reloads plugins."""

    def __init__(self, plugins_dir: Path) -> None:
        """Initialize the watcher.

        Args:
            plugins_dir: Directory to watch for plugin files
        """
        super().__init__()
        self.plugins_dir = plugins_dir

    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events.

        Args:
            event: Filesystem event
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix == ".py":
            print(f"New plugin detected: {file_path.name}")
            plugin_registry.load_file(file_path)

    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events.

        Args:
            event: Filesystem event
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix == ".py":
            print(f"Plugin modified: {file_path.name}")
            # Reload the plugin
            plugin_registry.load_file(file_path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events.

        Args:
            event: Filesystem event
        """
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix == ".py":
            # Find and unload the plugin
            plugin_name = file_path.stem
            plugin_registry.unload(plugin_name)
            print(f"Plugin unloaded: {plugin_name}")
