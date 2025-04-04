import json
from pathlib import Path
from typing import Dict

import toml
import yaml


def load_config_file(config_path: str) -> Dict:
    path = Path(config_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(path, "r") as f:
        if path.suffix in [".yml", ".yaml"]:
            return yaml.safe_load(f)
        elif path.suffix == ".json":
            return json.load(f)
        elif path.suffix == ".toml":
            return toml.load(f)
        else:
            raise ValueError(f"Unsupported config format: {path.suffix}")


def merge_config(cli_args: Dict, file_config: Dict) -> Dict:
    return {**file_config, **{k: v for k, v in cli_args.items() if v is not None}}
