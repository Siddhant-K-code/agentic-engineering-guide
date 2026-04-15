import os
import json
from pathlib import Path

def read_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path) as f:
        return json.load(f)

def list_files(directory: str) -> list:
    return [str(p) for p in Path(directory).iterdir()]
