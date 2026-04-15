import json
from typing import Any

def load_json(path: str) -> Any:
    with open(path) as f:
        return json.load(f)

def dump_json(data: Any, path: str, indent: int = 2) -> None:
    with open(path, "w") as f:
        json.dump(data, f, indent=indent)
