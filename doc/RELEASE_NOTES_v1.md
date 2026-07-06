# Procyl v1.0.0 Release Notes

**Release Date:** July 6, 2026

## 🎉 What's New

Procyl v1.0.0 is a major release with comprehensive refactoring and new features. This version introduces intelligent dependency management, environment setup, and parallel execution capabilities.

### Major Features

#### 1️⃣ **Automatic Dependency Detection**
- Scans Python code using AST analysis
- Detects external packages (filters stdlib automatically)
- Integrated with environment setup

```python
worker = procyl.create("demo", '''
import requests    # Detected
import numpy       # Detected  
import os          # Filtered (stdlib)
''')
print(worker.data.dependencies)
# Output: {'requests', 'numpy'}
```

#### 2️⃣ **Smart Environment Management**
- New `procyl.prepare()` function
- One-time venv setup for all workers
- Version constraint support
- Requirements.txt support

```python
# Auto-detect all dependencies
procyl.prepare()

# With constraints
procyl.prepare(constraints={
    "requests": "==2.32.3",
    "numpy": ">=2.3,<3"
})

# From file
procyl.prepare(requirements="requirements.txt")
```

#### 3️⃣ **Worker Metadata System**
- New `.data` property with 11 properties
- Hash, compiler, platform, size, and more
- Real-time running status

```python
worker = procyl.create("app", code)
print(worker.data.hash)              # Code SHA256
print(worker.data.dependencies)      # External packages
print(worker.data.python_version)    # Current Python
print(worker.data.platform)          # OS-Architecture
print(worker.data.running)           # Is executing?
```

#### 4️⃣ **Parallel Execution**
- New `worker.run(count=N)` method
- Leverages multiprocessing.Pool
- Returns list of outputs

```python
# Run 8 times in parallel
results = worker.run(count=8)
print(f"Executed {len(results)} times")
```

#### 5️⃣ **Worker Verification**
- New `worker.verify()` method
- Syntax validation
- Dependency listing
- Issue detection

```python
result = worker.verify()
print(result)
# {
#     'name': 'worker_name',
#     'valid': True,
#     'issues': [],
#     'dependencies': ['requests'],
#     'compiled': False
# }
```

### Breaking Changes ⚠️

**`procyl.create()` now returns `Worker` object instead of `Dict`**

```python
# OLD (v0.1.1)
result = procyl.create("app", code)
print(result["name"])

# NEW (v1.0.0)
worker = procyl.create("app", code)
print(worker.name)
print(worker.data.hash)
```

### New Modules

1. **`procyl.dependencies`** - Dependency scanning and parsing
2. **`procyl.environment`** - Environment management and venv handling

### Disk Efficiency

- `.procyl/` directory: ~50-300MB (depending on dependencies)
- One-time setup for all workers
- Minimal overhead per worker

```
.procyl/
├── env/           # Shared venv
├── .metadata/     # Worker metadata
└── metadata.json  # Environment info
```

### Performance Improvements

- **AST-based dependency detection** - Sub-millisecond scans
- **Multiprocessing pool** - Near-linear scaling with core count
- **Lazy venv creation** - Only created when needed

## 📊 Statistics

- **New Functions:** 2 (`procyl.prepare()`, `worker.run()`)
- **New Methods:** 2 (`worker.verify()`, `worker.data`)
- **New Modules:** 2 (`dependencies`, `environment`)
- **Code Lines Added:** ~1,200
- **Test Coverage:** 18+ test cases
- **Documentation:** 500+ lines

## 🔄 Migration Path

For users upgrading from v0.1.1:

1. Replace `dict` assignments with Worker objects
2. Add `procyl.prepare()` in initialization
3. Update `.to_dict()` calls to use `.data` property
4. Use `.run(count=N)` for parallel execution

See [MIGRATION_v1.md](MIGRATION_v1.md) for detailed guide.

## 🧪 Testing

All features tested:
- ✅ Worker creation and management
- ✅ Dependency detection (15+ stdlib modules)
- ✅ Environment setup and venv creation
- ✅ Metadata access and properties
- ✅ Worker verification
- ✅ Parallel execution
- ✅ Multiple execution modes

## 📦 Dependencies

New dependency:
- `psutil>=5.9.0` - Process status monitoring

## 🚀 Getting Started

```bash
# Install
pip install procyl

# Quick test
python3 -c "
import procyl
w = procyl.create('hello', 'print(\"v1.0.0\")')
procyl.prepare()
print(procyl.run('hello'))
"
```

## 📚 Documentation

- **README.md** - Main documentation
- **README_v1.md** - Full API reference  
- **MIGRATION_v1.md** - Migration guide
- **CHANGELOG_v1.md** - Detailed changelog
- **examples/demo.py** - Comprehensive example

## ⚡ Performance Numbers

On an 8-core system:

| Operation | Time |
|-----------|------|
| Worker creation | ~1ms |
| Dependency scan | ~2ms |
| Parallel run (8x) | ~100ms (per execution) |
| Environment setup | ~5-30s (once) |

## 🐛 Known Limitations

1. **Dynamic imports not detected** - Only top-level imports scanned
2. **Platform-specific artifacts** - Compiled binaries per OS
3. **Manual cleanup** - Venv persists to reuse dependencies

## 🎯 Future Roadmap

- GPU support for parallel workers
- Docker containerization
- Remote worker execution
- Advanced dependency resolution
- Worker caching and reuse

## 💬 Feedback

Report issues: [GitHub Issues](https://github.com/yo-le-zz/Procyl/issues)

---

**Procyl v1.0.0** marks the transition to a production-ready system with intelligent dependency management and parallel execution. Upgrade today to experience the improvements!

Created by [yolezz](https://github.com/yo-le-zz)
