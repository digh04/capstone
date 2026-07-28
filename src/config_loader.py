"""Load project configuration from config.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETUP_DIR = PROJECT_ROOT / "setup"
CONFIG_PATH = SETUP_DIR / "config.yaml"


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or CONFIG_PATH
    with path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    config["_project_root"] = PROJECT_ROOT
    return config


def resolve_path(config: dict[str, Any], relative: str) -> Path:
    return config["_project_root"] / relative
