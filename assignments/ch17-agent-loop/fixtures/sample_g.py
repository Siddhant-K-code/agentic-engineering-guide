from pathlib import Path

def read_file(path: str) -> str:
    return Path(path).read_text()

def write_file(path: str, content: str) -> None:
    Path(path).write_text(content)
