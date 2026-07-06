from __future__ import annotations

import hashlib
import json
import os
import platform
import psutil
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple
from multiprocessing import Pool

from .dependencies import get_dependencies_from_code


# Module-level function for multiprocessing (must be picklable)
def _run_worker_once(args: Tuple[str, Optional[str], Optional[List[str]], Optional[int]]) -> str:
    """Execute a worker code or artifact once. Used for multiprocessing."""
    code, artifact_path, args_list, timeout = args
    
    from .runner import run_code, run_compiled
    
    if artifact_path and os.path.exists(artifact_path):
        return run_compiled(artifact_path, args_list or [], timeout_seconds=timeout)
    return run_code(code, args_list or [], timeout_seconds=timeout)


class WorkerData:
    """Metadata about a worker."""

    def __init__(self, worker: Worker):
        self._worker = worker
        self._metadata_path = None
        self._load_metadata()

    def _load_metadata(self) -> None:
        """Load metadata from disk if exists."""
        if self._worker.artifact_path:
            base = os.path.dirname(self._worker.artifact_path)
            meta_file = os.path.join(base, f"{self._worker.name}.meta.json")
            if os.path.exists(meta_file):
                self._metadata_path = meta_file
                return
        
        # Try .procyl/.metadata
        meta_file = os.path.join(".procyl", ".metadata", f"{self._worker.name}.json")
        if os.path.exists(meta_file):
            self._metadata_path = meta_file

    def _get_metadata(self) -> Dict:
        """Get metadata dictionary."""
        if self._metadata_path and os.path.exists(self._metadata_path):
            with open(self._metadata_path) as f:
                return json.load(f)
        return {}

    def _save_metadata(self, data: Dict) -> None:
        """Save metadata to disk."""
        os.makedirs(".procyl/.metadata", exist_ok=True)
        meta_file = os.path.join(".procyl", ".metadata", f"{self._worker.name}.json")
        with open(meta_file, "w") as f:
            json.dump(data, f, indent=2)
        self._metadata_path = meta_file

    @property
    def hash(self) -> str:
        """Hash of the worker code."""
        return hashlib.sha256(self._worker.code.encode()).hexdigest()[:16]

    @property
    def compiler(self) -> str:
        """Compiler used."""
        return self._worker.compiler

    @property
    def compiled(self) -> bool:
        """Whether worker is compiled."""
        return bool(self._worker.artifact_path and os.path.exists(self._worker.artifact_path))

    @property
    def created_at(self) -> Optional[str]:
        """Creation timestamp."""
        meta = self._get_metadata()
        return meta.get("created_at")

    @property
    def last_build(self) -> Optional[str]:
        """Last build timestamp."""
        if not self.compiled:
            return None
        return os.path.getctime(self._worker.artifact_path) if self._worker.artifact_path else None

    @property
    def dependencies(self) -> Set[str]:
        """External dependencies."""
        return get_dependencies_from_code(self._worker.code)

    @property
    def python_version(self) -> str:
        """Python version."""
        return sys.version.split()[0]

    @property
    def platform(self) -> str:
        """Platform."""
        return f"{platform.system()}-{platform.machine()}"

    @property
    def path(self) -> Optional[str]:
        """Path to compiled artifact."""
        return self._worker.artifact_path

    @property
    def size(self) -> int:
        """Size in bytes of compiled artifact."""
        if self._worker.artifact_path and os.path.exists(self._worker.artifact_path):
            return os.path.getsize(self._worker.artifact_path)
        return 0

    @property
    def pid(self) -> Optional[int]:
        """Process ID if running."""
        return getattr(self._worker, "_current_pid", None)

    @property
    def running(self) -> bool:
        """Whether worker is currently running."""
        pid = self.pid
        if pid is None:
            return False
        try:
            return psutil.pid_exists(pid)
        except:
            return False


@dataclass
class Worker:
    name: str
    code: str
    icon: Optional[str] = None
    args: List[str] = field(default_factory=list)
    compiler: str = "auto"
    output_dir: Optional[str] = None
    state: str = "ready"
    artifact_path: Optional[str] = None
    timeout_seconds: Optional[int] = None
    auto_delete_after: Optional[int] = None
    compile_args: List[str] = field(default_factory=list)
    thread: Optional[threading.Thread] = None
    progress_percent: int = 0
    progress_message: str = "idle"
    _data: Optional[WorkerData] = field(default=None, init=False, repr=False)
    _current_pid: Optional[int] = field(default=None, init=False, repr=False)

    @property
    def data(self) -> WorkerData:
        """Get worker metadata."""
        if self._data is None:
            self._data = WorkerData(self)
        return self._data

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "icon": self.icon,
            "args": list(self.args),
            "compiler": self.compiler,
            "output_dir": self.output_dir,
            "state": self.state,
            "artifact_path": self.artifact_path,
            "timeout_seconds": self.timeout_seconds,
            "auto_delete_after": self.auto_delete_after,
            "compile_args": list(self.compile_args),
            "progress_percent": self.progress_percent,
            "progress_message": self.progress_message,
        }

    def verify(self) -> Dict[str, any]:
        """Verify worker integrity and compile status.
        
        Returns:
            Dict with verification results
        """
        results = {
            "name": self.name,
            "valid": True,
            "issues": [],
        }

        # Check code
        try:
            compile(self.code, self.name, "exec")
        except SyntaxError as e:
            results["valid"] = False
            results["issues"].append(f"Syntax error: {e}")

        # Check dependencies availability
        try:
            deps = self.data.dependencies
            if deps:
                results["dependencies"] = list(deps)
        except Exception as e:
            results["issues"].append(f"Dependency scan error: {e}")

        # Check compiled artifact
        if self.artifact_path:
            if not os.path.exists(self.artifact_path):
                results["valid"] = False
                results["issues"].append(f"Artifact not found: {self.artifact_path}")
            else:
                results["compiled"] = True
                results["artifact_size"] = os.path.getsize(self.artifact_path)

        return results

    def run(self, count: int = 1, args: Optional[List[str]] = None) -> List[str]:
        """Run worker multiple times in parallel.
        
        Args:
            count: Number of parallel executions
            args: Arguments to pass (overrides default)
            
        Returns:
            List of outputs from each execution
        """
        effective_args = list(args if args is not None else self.args)

        if count <= 1:
            # Single execution - don't need multiprocessing
            return [_run_worker_once(
                (self.code, self.artifact_path, effective_args, self.timeout_seconds)
            )]

        # Prepare arguments for pool
        pool_args = [
            (self.code, self.artifact_path, effective_args, self.timeout_seconds)
            for _ in range(count)
        ]

        # Try multiprocessing, fall back to sequential if needed
        try:
            with Pool(processes=min(count, os.cpu_count() or 1)) as pool:
                results = pool.map(_run_worker_once, pool_args)
            return results
        except (RuntimeError, ConnectionResetError, Exception):
            # Fallback for environments where multiprocessing doesn't work well
            return [_run_worker_once(args_tuple) for args_tuple in pool_args]


def _choose_compiler(compiler: Optional[str]) -> str:
    if compiler in {"python", "pyinstaller", "nuitka"}:
        return compiler
    if compiler == "auto":
        if shutil.which("nuitka"):
            return "nuitka"
        if shutil.which("pyinstaller"):
            return "pyinstaller"
    return "python"


def _build_command(source_path: str, target_dir: str, compiler: str, worker: Worker) -> List[str]:
    base_name = worker.name.replace(" ", "_")
    if compiler == "pyinstaller":
        command = ["pyinstaller", "--onefile", "--distpath", target_dir, "--name", base_name]
        if worker.icon:
            command.extend(["--icon", worker.icon])
        command.extend(worker.compile_args)
        command.append(source_path)
        return command

    command = ["nuitka", "--onefile", "--output-dir", target_dir, "--output-filename", f"{base_name}.exe"]
    if worker.icon:
        command.extend(["--windows-icon-from-ico", worker.icon])
    command.extend(worker.compile_args)
    command.append(source_path)
    return command


def _compile_source(source_path: str, output_dir: Optional[str], compiler: Optional[str], runtime: bool, worker: Worker) -> dict:
    selected_compiler = _choose_compiler(compiler)
    target_dir = output_dir or tempfile.mkdtemp(prefix="procyl-", dir=tempfile.gettempdir())
    os.makedirs(target_dir, exist_ok=True)
    worker.progress_percent = 10
    worker.progress_message = "Preparing build"
    time.sleep(0.01)

    if selected_compiler == "python":
        worker.progress_percent = 60
        worker.progress_message = "Copying source"
        artifact = os.path.join(target_dir, f"{worker.name}.py")
        shutil.copy2(source_path, artifact)
        worker.progress_percent = 100
        worker.progress_message = "Build ready"
        return {
            "state": "compiled" if not runtime else "ready",
            "artifact_path": artifact,
            "compiler": selected_compiler,
            "output_dir": target_dir,
            "output": "Python source copied for execution",
        }

    worker.progress_percent = 30
    worker.progress_message = f"Running {selected_compiler}"
    command = _build_command(source_path, target_dir, selected_compiler, worker)
    result = subprocess.run(command, capture_output=True, text=True)
    worker.progress_percent = 80
    worker.progress_message = "Collecting artifact"
    artifact = os.path.join(target_dir, f"{worker.name.replace(' ', '_')}.exe")
    if selected_compiler == "pyinstaller" and not os.path.exists(artifact):
        artifact = os.path.join(target_dir, "dist", f"{worker.name.replace(' ', '_')}.exe")
    if not os.path.exists(artifact):
        candidate_paths = [
            artifact,
            os.path.join(target_dir, "dist", "worker.exe"),
            os.path.join(target_dir, "dist", f"{worker.name.replace(' ', '_')}.exe"),
            os.path.join(target_dir, "demo.exe"),
            os.path.join(os.path.dirname(target_dir), "demo.exe"),
        ]
        for candidate in candidate_paths:
            if candidate and os.path.exists(candidate):
                artifact = candidate
                break
        else:
            artifact = None

        if artifact is None:
            search_roots = [target_dir]
            parent = os.path.dirname(target_dir)
            for _ in range(2):
                if parent and parent not in search_roots:
                    search_roots.append(parent)
                    parent = os.path.dirname(parent)
            for root in search_roots:
                if not os.path.isdir(root):
                    continue
                for current_root, _, files in os.walk(root):
                    for filename in sorted(files):
                        if filename.lower().endswith(".exe"):
                            artifact = os.path.join(current_root, filename)
                            break
                    if artifact:
                        break
                if artifact:
                    break

    worker.progress_percent = 100 if result.returncode == 0 else 0
    worker.progress_message = "Build finished" if result.returncode == 0 else "Build failed"
    if artifact and os.path.exists(artifact):
        worker.artifact_path = artifact
    elif selected_compiler == "pyinstaller" and os.path.exists(os.path.join(target_dir, "dist", "worker.exe")):
        worker.artifact_path = os.path.join(target_dir, "dist", "worker.exe")
    elif os.path.exists(os.path.join(target_dir, "demo.exe")):
        worker.artifact_path = os.path.join(target_dir, "demo.exe")

    return {
        "state": "compiled" if result.returncode == 0 else "failed",
        "artifact_path": worker.artifact_path,
        "compiler": selected_compiler,
        "output_dir": target_dir,
        "output": result.stdout + result.stderr,
    }


def compile_worker(worker, output_dir: Optional[str] = None, compiler: Optional[str] = None, runtime: bool = False) -> dict:
    import tempfile
    from .runner import run_code, schedule_cleanup

    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as handle:
        handle.write(worker.code)
        source_path = handle.name

    try:
        worker.state = "compiling"
        worker.progress_percent = 0
        worker.progress_message = "Starting build"
        result = _compile_source(source_path, output_dir, compiler, runtime, worker)
        worker.state = result["state"]
        worker.artifact_path = result.get("artifact_path")
        if runtime:
            worker.progress_percent = 100
            worker.progress_message = "Running compiled artifact"
            artifact = result.get("artifact_path") or worker.artifact_path
            if artifact and os.path.exists(artifact):
                from .runner import run_compiled
                output = run_compiled(artifact, worker.args, timeout_seconds=worker.timeout_seconds)
            else:
                from .runner import run_code
                output = run_code(worker.code, worker.args, timeout_seconds=worker.timeout_seconds)
            result["output"] = output or ""
        if worker.artifact_path and worker.auto_delete_after:
            schedule_cleanup(worker.artifact_path, worker.auto_delete_after)
        return {**worker.to_dict(), **result}
    finally:
        if os.path.exists(source_path):
            os.remove(source_path)
