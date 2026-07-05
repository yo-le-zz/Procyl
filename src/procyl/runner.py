import os
import subprocess
import sys
import tempfile
import threading
from typing import List, Optional


def _run_command(command: List[str], timeout_seconds: Optional[int] = None) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=timeout_seconds)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired as exc:
        return f"Process timed out after {timeout_seconds} seconds.\n{exc.stdout or ''}{exc.stderr or ''}"


def run_code(code: str, args: Optional[List[str]] = None, timeout_seconds: Optional[int] = None) -> str:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as handle:
        handle.write(code)
        path = handle.name

    try:
        command = [sys.executable, path]
        if args:
            command.extend(args)
        return _run_command(command, timeout_seconds=timeout_seconds)
    finally:
        os.remove(path)


def run_compiled(path: str, args: Optional[List[str]] = None, timeout_seconds: Optional[int] = None) -> str:
    if path.lower().endswith(".py"):
        command = [sys.executable, path]
    else:
        command = [path]
    if args:
        command.extend(args)
    return _run_command(command, timeout_seconds=timeout_seconds)


def schedule_cleanup(path: str, delay_seconds: int) -> threading.Thread:
    def _cleanup() -> None:
        import time
        time.sleep(delay_seconds)
        if os.path.exists(path):
            os.remove(path)

    thread = threading.Thread(target=_cleanup, daemon=True)
    thread.start()
    return thread