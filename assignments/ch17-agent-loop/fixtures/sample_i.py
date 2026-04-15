import subprocess
from typing import List

def run_command(cmd: List[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def git_status(repo_path: str = ".") -> str:
    return run_command(["git", "-C", repo_path, "status", "--short"])
