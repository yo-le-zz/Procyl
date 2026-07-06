# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-07-06

### ✨ Major Features Added

#### Automatic Dependency Detection
- Scans Python code using AST analysis
- Automatically detects external package dependencies
- Filters out standard library modules
- Integrated with environment setup

#### Worker Metadata System (`.data` property)
- `worker.data.hash` - SHA256 hash of worker code (16 chars)
- `worker.data.compiler` - Compiler type used
- `worker.data.compiled` - Compilation status
- `worker.data.created_at` - Creation timestamp
- `worker.data.last_build` - Last build timestamp
- `worker.data.dependencies` - Set of external packages
- `worker.data.python_version` - Python version string
- `worker.data.platform` - Platform identifier (OS-Architecture)
- `worker.data.path` - Path to compiled artifact
- `worker.data.size` - Artifact size in bytes
- `worker.data.pid` - Process ID if running
- `worker.data.running` - Current running status

#### Environment Management System
- New `procyl.prepare()` function for one-time environment setup
- Supports version constraints: `{"package": "==1.0.0", "numpy": ">=2.3,<3"}`
- Supports requirements.txt files
- Creates isolated venv in `.procyl/env/`
- Metadata stored in `.procyl/metadata.json`

#### Worker Verification
- New `worker.verify()` method
- Validates Python syntax
- Checks compilation status
- Lists all dependencies
- Reports any issues

#### Parallel Execution
- New `worker.run(count=N)` method
- Executes worker N times in parallel using `multiprocessing.Pool`
- Optional custom arguments per execution
- Returns list of outputs

#### New Modules
- `procyl.dependencies` - Dependency scanning with AST analysis
- `procyl.environment` - Environment management and venv handling

### 🔄 API Changes

#### Breaking Changes
- `procyl.create()` now returns `Worker` object instead of `Dict`
  - **Reason:** Enable method calls and property access
  - **Migration:** Update all `.create()` calls to capture Worker object

#### Improved APIs
- `procyl.prepare()` - NEW - environment setup
- `worker.verify()` - NEW - validation method
- `worker.run(count=N)` - NEW - parallel execution
- `worker.data` - NEW - metadata property

#### Unchanged APIs
- `procyl.run(name, args)` - still returns output string
- `procyl.status(name)` - still returns dict
- `procyl.delete(name)` - still returns dict
- `procyl.precompile(...)` - still returns dict
- `procyl.runtime_compile(...)` - still returns dict

### 📦 Dependencies
- Added `psutil>=5.9.0` - for process management and running status

### 🎯 Improvements
- Minimal disk footprint for environments
- One-time environment setup (efficient for multiple workers)
- Better code organization with separate modules
- Comprehensive metadata tracking
- Parallel execution for performance

### 📚 Documentation
- Complete API reference in README_v1.md
- Migration guide in MIGRATION_v1.md
- Comprehensive inline docstrings
- Feature examples in examples/demo.py

### ✅ Testing
- New test suite in tests/test_core_v1.py
- Coverage for:
  - Worker creation and management
  - Dependency detection
  - Metadata access
  - Verification system
  - Parallel execution
  - Environment preparation
  - Multiple execution modes

### 🐛 Known Limitations
- Dependency detection uses top-level imports only
  - Dynamic imports (inside functions) are not detected
- Environment cleanup must be manual (to preserve venv)
- Compiled artifacts are platform-specific

## [0.1.1] - Previous Version

Previous release features and functionality (legacy API).

---

## Upgrade Guide

See [MIGRATION_v1.md](MIGRATION_v1.md) for detailed migration instructions.

### Quick Start for v1.0.0

```python
import procyl

# Create workers - now returns Worker objects
worker = procyl.create("demo", code)

# Prepare environment once
procyl.prepare()

# Access metadata
print(worker.data.dependencies)
print(worker.data.python_version)

# Verify worker
print(worker.verify())

# Run once or in parallel
output = procyl.run("demo")
results = worker.run(count=8)
```
