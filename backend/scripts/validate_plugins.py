from pathlib import Path


def main() -> None:
    plugins_dir = Path(__file__).resolve().parents[1] / "plugins"
    plugin_files = sorted(p.name for p in plugins_dir.glob("*.py") if p.name != "__init__.py")
    print(f"Plugin directory: {plugins_dir}")
    print(f"Detected plugins: {plugin_files}")


if __name__ == "__main__":
    main()
