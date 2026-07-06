# Procyl v1.0.0

**A lightweight, intelligent worker system for creating, compiling, running, and managing Python-based processes.**

> Procyl simplifies the management of isolated Python workers with automatic dependency detection, environment management, and parallel execution support.

## ✨ Features

- 🔧 **Automatic Dependency Detection** - Scans code for external packages (not stdlib)
- 🎯 **Smart Environment Management** - One-time environment setup via `procyl.prepare()`
- 🚀 **Multiple Execution Modes** - Python source, PyInstaller, or Nuitka compilation
- ⚡ **Parallel Execution** - Run workers multiple times simultaneously
- 📊 **Rich Metadata** - Access worker info via `.data` property
- 🛡️ **Verification** - Built-in worker integrity checks
- 📦 **Minimal Footprint** - Lightweight, disk-efficient design
- 🔄 **Version Control** - Support for specific package versions and requirements files

## 📦 Installation

```bash
pip install procyl
```

For compilation support:
```bash
pip install procyl[compile]
```

## 🚀 Quick Start

### 1. Create Workers

Workers are Python functions executed in isolated processes:

```python
import procyl

# Create a simple worker
worker = procyl.create(
    "greet",
    '''
import sys
print(f"Hello, {sys.argv[1]}!")
'''
)
```

### 2. Prepare Environment

Install all dependencies used by workers:

```python
# Automatic - scans all workers
procyl.prepare()

# With specific versions
procyl.prepare(constraints={
    "requests": "==2.32.3",
    "numpy": ">=2.3,<3"
})

# From requirements file
procyl.prepare(requirements="requirements.txt")
```

### 3. Access Worker Metadata

```python
print(worker.data.hash)              # Code hash
print(worker.data.compiler)          # Compiler used
print(worker.data.compiled)          # Compilation status
print(worker.data.dependencies)      # External dependencies
print(worker.data.python_version)    # Python version
print(worker.data.platform)          # Platform info
print(worker.data.path)              # Artifact path
print(worker.data.size)              # Artifact size
print(worker.data.running)           # Is running?
```

### 4. Verify Workers

```python
result = worker.verify()
print(result)
# {
#     'name': 'greet',
#     'valid': True,
#     'issues': [],
#     'dependencies': ['requests', 'numpy']
# }
```

### 5. Run Workers

```python
# Single execution
output = procyl.run("greet", args=["Alice"])

# Multiple parallel executions
results = worker.run(count=8, args=["Bob"])
for output in results:
    print(output)
```

## 📚 API Reference

### `procyl.create()`

Create a new worker.

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

**Returns:** `Worker` object

### `procyl.prepare()`

Prepare the Python environment with dependencies.

```python
success = procyl.prepare(
    constraints: Optional[Dict[str, str]] = None,
    requirements: Optional[str] = None,
)
```

**Parameters:**
- `constraints`: Dict of package version constraints
- `requirements`: Path to requirements.txt file

**Returns:** `bool` - Success status

### `worker.data`

Access worker metadata (read-only).

**Properties:**
- `hash` - SHA256 hash of code (16 chars)
- `compiler` - Compiler used
- `compiled` - Whether compiled
- `created_at` - Creation timestamp
- `last_build` - Last build timestamp
- `dependencies` - Set of external package names
- `python_version` - Python version
- `platform` - Platform string
- `path` - Path to artifact
- `size` - Artifact size in bytes
- `pid` - Process ID (if running)
- `running` - Whether currently running

### `worker.verify()`

Verify worker integrity.

```python
result = worker.verify()
# Returns dict with:
# - 'name': worker name
# - 'valid': boolean
# - 'issues': list of issues
# - 'compiled': (optional)
# - 'artifact_size': (optional)
# - 'dependencies': (optional)
```

### `worker.run()`

Execute worker once or multiple times in parallel.

```python
results = worker.run(
    count: int = 1,                     # Number of parallel executions
    args: Optional[List[str]] = None,   # Arguments (overrides default)
)
```

**Returns:** `List[str]` - List of outputs

### `procyl.run()`

Execute a worker by name.

```python
output = procyl.run(
    name: str,
    args: Optional[List[str]] = None,
)
```

### `procyl.status()`

Get worker status.

```python
status = procyl.status(name: str)
```

### `procyl.delete()`

Delete a worker.

```python
result = procyl.delete(name: str)
```

### `procyl.precompile()`

Compile a worker ahead of time.

```python
result = procyl.precompile(
    name: str,
    output_dir: Optional[str] = None,
    compiler: Optional[str] = None,
    thread: bool = False,
)
```

## 📁 File Structure

```
.procyl/                    # Created by prepare()
├── env/                    # Python venv
│   ├── bin/               # Python executables
│   ├── lib/               # Installed packages
│   └── ...
├── .metadata/             # Worker metadata
└── metadata.json          # Environment info
```

## 🔍 Automatic Dependency Scanning

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

## 🎯 Use Cases

### Multi-threaded Workers
```python
worker = procyl.create("compute", "print(sum(range(1000)))")
results = worker.run(count=8)
print(f"Computed {len(results)} times in parallel")
```

### Version-Pinned Dependencies
```python
procyl.prepare(constraints={
    "tensorflow": "==2.13.0",
    "numpy": "<2.0"
})
```

### Compiled Executables
```python
worker = procyl.create("app", code)
procyl.precompile("app", compiler="pyinstaller", output_dir="./dist")
```

## 📝 Examples

See [examples/demo.py](examples/demo.py) for a comprehensive example:

```bash
python examples/demo.py
```

## 🧪 Testing

Run tests:

```bash
pytest tests/test_core_v1.py -v
```

Run verification:

```bash
python verify.py
```

## 📄 Documentation

- [CHANGELOG_v1.md](CHANGELOG_v1.md) - What's new in v1.0.0
- [MIGRATION_v1.md](MIGRATION_v1.md) - Migration guide from v0.1.1
- [README_v1.md](README_v1.md) - Full API documentation

## 📄 License

MIT

## 👤 Author

yolezz

---

**Procyl v1.0.0** - Intelligent Python Worker Management
