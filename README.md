# Procyl

Procyl is a lightweight Python worker system for creating, compiling, running, and managing small executable processes from Python code. It is designed for developers who want a simple API for building and launching workers with optional compilation, timeouts, cleanup rules, and progress tracking.

Created by [yo-le-zz](https://github.com/yo-le-zz).

## Features

- Create named workers with Python code, optional icon, arguments and compiler preferences
- Run workers directly from temporary Python files
- Precompile workers into persistent `.exe` artifacts with PyInstaller or Nuitka
- Runtime compile workers on-the-fly for one-shot execution
- Configure timeouts so a process is stopped if it hangs
- Automatically delete generated artifacts after a chosen delay
- Track compilation progress through the worker status
- Run multiple workers in parallel and compile several workers in threads

## Installation

```bash
pip install .
```

To install optional compile backends:

```bash
pip install .[compile]
```

## Quick start

```python
import procyl

procyl.create(
    "hello",
    'print("Hello from Procyl")',
    icon="hello.png",
    args=["--demo"],
    timeout_seconds=5,
    auto_delete_after=30,
)

print(procyl.run("hello"))
print(procyl.status("hello"))
procyl.precompile("hello", output_dir="./dist", compiler="pyinstaller")
procyl.delete("hello")
```

## Core API

- `create(name, code, icon=None, args=None, compiler="auto", output_dir=None, timeout_seconds=None, auto_delete_after=None, compile_args=None)`
- `run(name, args=None)`
- `precompile(name, output_dir=None, compiler=None, thread=False)`
- `runtime_compile(name, compiler=None)`
- `status(name)`
- `delete(name)`

## Compilation modes

- `precompile(...)` keeps a build artifact on disk.
- `runtime_compile(...)` compiles and runs once, then uses temporary files for the build.
- `create(..., compiler="auto")` accepts `python`, `pyinstaller`, `nuitka`, or `auto`.

## Examples

Several ready-to-run examples are available in the [examples](examples) folder:

- [examples/demo.py](examples/demo.py)
- [examples/threaded_compile.py](examples/threaded_compile.py)
- [examples/runtime_worker.py](examples/runtime_worker.py)
- [examples/parallel_workers.py](examples/parallel_workers.py)

## Testing

Run the test suite with:

```bash
pytest -q
```

## Project structure

- [src/procyl/core.py](src/procyl/core.py) for the public API
- [src/procyl/worker.py](src/procyl/worker.py) for worker state and compilation logic
- [src/procyl/runner.py](src/procyl/runner.py) for subprocess execution and cleanup
- [tests](tests) for regression tests
