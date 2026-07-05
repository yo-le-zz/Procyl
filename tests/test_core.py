import subprocess
import time

import procyl


def test_create_and_run():
    worker = procyl.create(
        "t1",
        "print('ok')",
        icon="demo.ico",
        args=["hello"],
        compiler="pyinstaller",
        timeout_seconds=3,
        auto_delete_after=5,
    )
    assert worker["name"] == "t1"
    assert worker["state"] == "ready"
    assert worker["timeout_seconds"] == 3
    assert worker["auto_delete_after"] == 5
    output = procyl.run("t1")
    assert "ok" in output


def test_status_and_delete(tmp_path):
    procyl.create("t2", "print('x')")
    status = procyl.status("t2")
    assert status["exists"] is True
    assert status["state"] == "ready"

    artifact = tmp_path / "t2.exe"
    artifact.write_text("fake")
    procyl._workers["t2"].artifact_path = str(artifact)
    procyl.delete("t2")
    assert procyl.status("t2")["exists"] is False
    assert not artifact.exists()


def test_precompile_uses_pyinstaller_arguments(tmp_path, monkeypatch):
    calls = []

    def fake_run(command, capture_output=True, text=True):
        output_path = tmp_path / "demo.exe"
        output_path.write_text("fake exe")
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, stdout="built", stderr="")

    monkeypatch.setattr("procyl.worker.subprocess.run", fake_run)
    monkeypatch.setattr("procyl.worker.shutil.which", lambda name: "/usr/bin/pyinstaller" if name == "pyinstaller" else None)

    procyl.create("t3", "print('compiled')", icon="demo.ico", compiler="pyinstaller")
    result = procyl.precompile("t3", output_dir=str(tmp_path / "build"), compiler="pyinstaller")

    assert result["state"] == "compiled"
    assert result["artifact_path"].endswith(".exe")
    assert any("--name" in item for item in calls[0])
    assert any("demo.ico" in item for item in calls[0])


def test_runtime_compile_and_threaded_progress(tmp_path, monkeypatch):
    compile_calls = []

    def fake_compile_run(command, capture_output=True, text=True):
        compile_calls.append(command)
        artifact_path = tmp_path / "runtime.exe"
        artifact_path.write_text("fake exe")
        time.sleep(0.05)
        return subprocess.CompletedProcess(command, 0, stdout="built", stderr="")

    def fake_run(command, capture_output=True, text=True, timeout=None):
        if command and command[0].endswith(".exe"):
            return subprocess.CompletedProcess(command, 0, stdout="artifact-run", stderr="")
        return subprocess.CompletedProcess(command, 0, stdout="", stderr="")

    monkeypatch.setattr("procyl.worker.subprocess.run", fake_compile_run)
    monkeypatch.setattr("procyl.runner.subprocess.run", fake_run)

    procyl.create("t4", "print('runtime')", compiler="pyinstaller")
    procyl.precompile("t4", output_dir=str(tmp_path / "build"), compiler="pyinstaller", thread=True)

    for _ in range(10):
        status = procyl.status("t4")
        if status["state"] != "compiling":
            break
        time.sleep(0.01)

    status = procyl.status("t4")
    assert status["state"] in {"compiled", "ready", "failed"}
    assert status["progress_percent"] >= 0

    runtime_result = procyl.runtime_compile("t4", compiler="pyinstaller")
    assert "artifact-run" in runtime_result["output"]
    assert runtime_result["artifact_path"].endswith(".exe")


def test_parallel_creation_and_timeout(tmp_path):
    procyl.create("parallel-a", "print('a')", compiler="pyinstaller", timeout_seconds=2)
    procyl.create("parallel-b", "print('b')", compiler="pyinstaller", timeout_seconds=2)

    status_a = procyl.status("parallel-a")
    status_b = procyl.status("parallel-b")

    assert status_a["timeout_seconds"] == 2
    assert status_b["timeout_seconds"] == 2
    assert status_a["name"] == "parallel-a"
    assert status_b["name"] == "parallel-b"


def test_delete_removes_artifact(tmp_path):
    artifact_path = tmp_path / "artifact.exe"
    artifact_path.write_text("fake")
    procyl.create("cleanup", "print('cleanup')")
    procyl._workers["cleanup"].artifact_path = str(artifact_path)
    result = procyl.delete("cleanup")
    assert result["deleted"] is True
    assert not artifact_path.exists()