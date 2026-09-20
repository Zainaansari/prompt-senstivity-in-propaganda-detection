import yaml
from pathlib import Path


def get_project_root() -> Path:
    """Return the repository root independent of the current working directory."""
    return Path(__file__).resolve().parents[1]

def load_config():
    config_path = get_project_root() / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)