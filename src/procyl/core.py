from __future__ import annotations

import os
import threading
from typing import Dict, List, Optional

from .runner import run_code, run_compiled
from .worker import Worker, compile_worker

_workers: Dict[str, Worker] = {}


def _get_worker(name: str) -> Worker:
    if name not in _workers:
        raise ValueError(f"Worker '{name}' not found")
    return _workers[name]


def create(
    name: str,
    code: str,
    icon: Optional[str] = None,
    args: Optional[List[str]] = None,
    compiler: str = "auto",
    output_dir: Optional[str] = None,
    timeout_seconds: Optional[int] = None,
    auto_delete_after: Optional[int] = None,
    compile_args: Optional[List[str]] = None,
) -> Dict[str, object]:
    worker = Worker(
        name=name.strip(),
        code=code,
        icon=icon,
        args=list(args or []),
        compiler=compiler,
        output_dir=output_dir,
        timeout_seconds=timeout_seconds,
        auto_delete_after=auto_delete_after,
        compile_args=list(compile_args or []),
    )
    _workers[worker.name] = worker
    return worker.to_dict()


def precompile(
    name: str,
    output_dir: Optional[str] = None,
    compiler: Optional[str] = None,
    thread: bool = False,
) -> Dict[str, object]:
    worker = _get_worker(name)
    if thread:
        worker.state = "compiling"
        worker.thread = threading.Thread(
            target=lambda: compile_worker(worker, output_dir=output_dir, compiler=compiler, runtime=False),
            daemon=True,
        )
        worker.thread.start()
        return worker.to_dict()
    return compile_worker(worker, output_dir=output_dir, compiler=compiler, runtime=False)


def runtime_compile(name: str, compiler: Optional[str] = None) -> Dict[str, object]:
    worker = _get_worker(name)
    return compile_worker(worker, output_dir=None, compiler=compiler, runtime=True)


def run(name: str, args: Optional[List[str]] = None) -> str:
    worker = _get_worker(name)
    if worker.state == "compiling":
        return "Worker is still compiling; retry later."

    effective_args = list(args or worker.args or [])
    if worker.artifact_path and os.path.exists(worker.artifact_path):
        return run_compiled(worker.artifact_path, effective_args, timeout_seconds=worker.timeout_seconds)
    return run_code(worker.code, effective_args, timeout_seconds=worker.timeout_seconds)


def status(name: str) -> Dict[str, object]:
    worker = _workers.get(name)
    if worker is None:
        return {"exists": False, "name": name, "state": "missing"}
    return {**worker.to_dict(), "exists": True}


def delete(name: str) -> Dict[str, object]:
    worker = _workers.pop(name, None)
    if worker is None:
        return {"deleted": False, "name": name, "state": "missing"}
    if worker.artifact_path and os.path.exists(worker.artifact_path):
        os.remove(worker.artifact_path)
    return {"deleted": True, "name": name, "state": "deleted"}