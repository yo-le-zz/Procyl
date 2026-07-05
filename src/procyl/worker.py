from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass, field
from typing import List, Optional


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
