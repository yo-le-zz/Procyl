# Procyl API Reference

Complete API documentation for Procyl v1.0.0.

## Table of Contents

- [procyl.create()](#procylcreate)
- [procyl.prepare()](#procylprepare)
- [procyl.run()](#procylrun)
- [procyl.status()](#procylstatus)
- [procyl.delete()](#procyldelete)
- [procyl.precompile()](#procylprecompile)
- [Worker.data](#workerdata)
- [Worker.verify()](#workerverify)
- [Worker.run()](#workerrun)

---

## procyl.create()

Create a new worker with isolated execution environment.

```python
worker = procyl.create(
    name: str,                          # Worker name
    code: str,                          # Python code
    icon: Optional[str] = None,         # Icon path
    args: Optional[List[str]] = None,   # Default arguments
    compiler: str = "auto",             # python/pyinstaller/nuitka/auto
    output_dir: Optional[str] = None,   # Output directory
    timeout_seconds: Optional[int] = None,
    auto_delete_after: Optional[int] = None,
    compile_args: Optional[List[str]] = None,
)
```

**Parameters:**
- `name` (str): Unique identifier for the worker
- `code` (str): Python code to execute
- `icon` (Optional[str]): Path to icon file for compiled executables
- `args` (Optional[List[str]]): Default command-line arguments
- `compiler` (str): Compilation method - "python", "pyinstaller", "nuitka", or "auto"
- `output_dir` (Optional[str]): Directory for compiled artifacts
- `timeout_seconds` (Optional[int]): Execution timeout in seconds
- `auto_delete_after` (Optional[int]): Auto-delete worker after N seconds
- `compile_args` (Optional[List[str]]): Additional compiler arguments

**Returns:** `Worker` object

**Example:**
```python
worker = procyl.create(
    "greet",
    '''
import sys
print(f"Hello, {sys.argv[1]}!")
''',
    args=["World"]
)
```

---

## procyl.prepare()

Prepare the Python environment with dependencies for all workers.

```python
success = procyl.prepare(
    constraints: Optional[Dict[str, str]] = None,
    requirements: Optional[str] = None,
)
```

**Parameters:**
- `constraints` (Optional[Dict[str, str]]): Package version constraints
  - Example: `{"requests": "==2.32.3", "numpy": ">=2.3,<3"}`
- `requirements` (Optional[str]): Path to requirements.txt file

**Returns:** `bool` - Success status

**Supported operators:** `==`, `>=`, `<=`, `>`, `<`, `!=`, `~=`

**Example:**
```python
# Automatic dependency scanning
procyl.prepare()

# With version constraints
procyl.prepare(constraints={
    "requests": "==2.32.3",
    "numpy": ">=2.3,<3"
})

# From requirements file
procyl.prepare(requirements="requirements.txt")
```

---

## procyl.run()

Execute a worker by name.

```python
output = procyl.run(
    name: str,
    args: Optional[List[str]] = None,
)
```

**Parameters:**
- `name` (str): Worker name to execute
- `args` (Optional[List[str]]): Command-line arguments (overrides default)

**Returns:** `str` - Output from worker execution

**Example:**
```python
output = procyl.run("greet", args=["Alice"])
print(output)  # "Hello, Alice!"
```

---

## procyl.status()

Get current status of a worker.

```python
status = procyl.status(name: str)
```

**Parameters:**
- `name` (str): Worker name

**Returns:** `dict` with keys:
- `exists` (bool): Whether worker exists
- `name` (str): Worker name
- `state` (str): "ready", "running", "compiling", "failed", or "missing"
- `progress_percent` (int): Compilation progress (0-100)
- `timeout_seconds` (int): Timeout setting
- `auto_delete_after` (int): Auto-delete setting

**Example:**
```python
status = procyl.status("my_worker")
print(status)
# {'exists': True, 'name': 'my_worker', 'state': 'ready', ...}
```

---

## procyl.delete()

Delete a worker and its artifacts.

```python
result = procyl.delete(name: str)
```

**Parameters:**
- `name` (str): Worker name to delete

**Returns:** `dict` with keys:
- `deleted` (bool): Success status
- `name` (str): Worker name

**Example:**
```python
result = procyl.delete("old_worker")
print(result)  # {'deleted': True, 'name': 'old_worker'}
```

---

## procyl.precompile()

Compile a worker ahead of time for distribution.

```python
result = procyl.precompile(
    name: str,
    output_dir: Optional[str] = None,
    compiler: Optional[str] = None,
    thread: bool = False,
)
```

**Parameters:**
- `name` (str): Worker name
- `output_dir` (Optional[str]): Output directory for artifact
- `compiler` (Optional[str]): Override compiler choice
- `thread` (bool): Run compilation in background thread

**Returns:** `dict` with compilation status

**Example:**
```python
# Synchronous compilation
result = procyl.precompile("app", compiler="pyinstaller", output_dir="./dist")

# Asynchronous compilation
result = procyl.precompile("app", thread=True)
# Check status later
status = procyl.status("app")
```

---

## Worker.data

Access worker metadata (read-only properties).

```python
worker.data.hash              # SHA256 hash of code (16 chars)
worker.data.compiler          # Compiler used
worker.data.compiled          # Whether compiled
worker.data.created_at        # Creation timestamp
worker.data.last_build        # Last build timestamp
worker.data.dependencies      # Set of external package names
worker.data.python_version    # Python version
worker.data.platform          # Platform string
worker.data.path              # Path to artifact
worker.data.size              # Artifact size in bytes
worker.data.pid               # Process ID (if running)
worker.data.running           # Whether currently running
```

**Properties:**
- `hash` (str): First 16 characters of SHA256 hash
- `compiler` (str): Compiler method used
- `compiled` (bool): Compilation status
- `created_at` (str): ISO timestamp of creation
- `last_build` (str): ISO timestamp of last build
- `dependencies` (set): External package names (excludes stdlib)
- `python_version` (str): Python version used
- `platform` (str): Platform identifier (e.g., "Linux-x86_64")
- `path` (str): Path to compiled artifact
- `size` (int): Artifact size in bytes
- `pid` (int): Process ID if currently running
- `running` (bool): Whether worker is executing

**Example:**
```python
print(f"Hash: {worker.data.hash}")
print(f"Deps: {worker.data.dependencies}")
print(f"Platform: {worker.data.platform}")
```

---

## Worker.verify()

Verify worker integrity and configuration.

```python
result = worker.verify()
```

**Returns:** `dict` with keys:
- `name` (str): Worker name
- `valid` (bool): Whether worker is valid
- `issues` (list): List of validation issues
- `compiled` (bool, optional): Compilation status
- `artifact_size` (int, optional): Artifact size in bytes
- `dependencies` (list, optional): Detected dependencies

**Example:**
```python
result = worker.verify()
if result['valid']:
    print("Worker is valid")
else:
    print(f"Issues: {result['issues']}")
```

---

## Worker.run()

Execute worker once or multiple times in parallel.

```python
results = worker.run(
    count: int = 1,                     # Number of parallel executions
    args: Optional[List[str]] = None,   # Arguments (overrides default)
)
```

**Parameters:**
- `count` (int): Number of parallel executions (default: 1)
- `args` (Optional[List[str]]): Command-line arguments

**Returns:** `List[str]` - List of outputs from each execution

**Example:**
```python
# Single execution
output = worker.run(count=1)

# Parallel execution (8 workers)
results = worker.run(count=8)
for i, output in enumerate(results):
    print(f"Worker {i}: {output}")

# With custom arguments
results = worker.run(count=2, args=["custom", "args"])
```

---

## File Structure

Procyl creates the following structure:

```
.procyl/                    # Created by prepare()
├── env/                    # Python venv
│   ├── bin/               # Python executables
│   ├── lib/               # Installed packages
│   └── ...
├── .metadata/             # Worker metadata
└── metadata.json          # Environment info
```

---

## Automatic Dependency Scanning

Procyl automatically scans code for external dependencies using AST analysis:

```python
worker = procyl.create("demo", '''
import requests
import numpy as np
import sys           # stdlib - ignored
import os            # stdlib - ignored

print("Hello")
''')

print(worker.data.dependencies)
# Output: {'requests', 'numpy'}
```

**Detection rules:**
- Scans `import` and `from ... import` statements
- Excludes Python standard library modules
- Includes external packages only
