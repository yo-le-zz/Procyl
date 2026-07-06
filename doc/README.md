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

## 📂 Project Structure

```
procyl/
├── src/procyl/
│   ├── __init__.py        # Main API
│   ├── core.py            # Core functions
│   ├── worker.py          # Worker & WorkerData classes
│   ├── runner.py          # Execution engine
│   ├── dependencies.py    # Dependency detection & parsing
│   ├── environment.py     # Environment management
│   └── utils.py           # Utilities
├── tests/
│   └── test_core.py       # All tests
├── examples/
│   ├── demo.py
│   ├── parallel_workers.py
│   └── runtime_worker.py
├── doc/
│   ├── README.md          # This file
│   ├── API.md             # Complete API reference
│   └── CHANGELOG.md       # Version history
└── pyproject.toml         # Project metadata
```

## 🔧 Configuration

### Environment

Procyl stores the virtual environment and metadata in `.procyl/`:

```
.procyl/
├── env/              # Virtual environment
├── metadata.json     # Worker metadata
└── .metadata/        # Metadata cache
```

### Version Constraints

Specify package versions:

```python
procyl.prepare(constraints={
    "numpy": ">=1.20,<2",
    "pandas": "==1.5.0",
    "requests": "~=2.32"
})
```

Supported operators: `==`, `>=`, `<=`, `>`, `<`, `!=`, `~=`

### Requirements File

```python
# requirements.txt
numpy==1.24.0
pandas>=1.5.0
requests~=2.32

# Load from file
procyl.prepare(requirements="requirements.txt")
```

## 🎯 Common Use Cases

### Parallel Data Processing

```python
import procyl

worker = procyl.create("processor", '''
import json
import sys
data = json.loads(sys.argv[1])
# Process data
print(json.dumps({"result": data}))
''')

procyl.prepare()

# Run 8 times in parallel
results = worker.run(count=8)
```

### Long-Running Tasks

```python
worker = procyl.create("task", '''
import time
for i in range(10):
    print(f"Step {i}")
    time.sleep(1)
''')

# Monitor execution
status = procyl.status("task")
output = procyl.run("task")
```

### Compiled Distribution

```python
worker = procyl.create("app", code, compiler="pyinstaller")

# Precompile for distribution
procyl.precompile("app", output_dir="./dist")

# Later: Run compiled artifact
output = procyl.run("app")
```

## 🐛 Troubleshooting

### Dependencies not detected

- Ensure `procyl.prepare()` is called after creating workers
- Check that imports use standard syntax: `import package` or `from package import`

### Environment errors

- Delete `.procyl/env/` and `.procyl/metadata.json` to reset
- Ensure Python 3.10+ is available
- Check pip is working: `pip list`

### Multiprocessing issues

- On Windows, ensure workers are created inside `if __name__ == "__main__":`
- Some CI/CD environments don't support multiprocessing; uses fallback

### Compilation failures

- Install PyInstaller: `pip install pyinstaller`
- Check artifact output: `procyl.status("worker_name")`

## 📖 Documentation

- **[API Reference](doc/API.md)** - Complete API documentation
- **[CHANGELOG](doc/CHANGELOG.md)** - Version history
- **[Examples](examples/)** - Working examples

## 🤝 Contributing

Bug reports and feature requests welcome on GitHub.

## 📄 License

MIT License - See LICENSE.txt

---

**Made with ❤️ by Procyl Contributors**
