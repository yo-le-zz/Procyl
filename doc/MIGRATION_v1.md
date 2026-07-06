# Migration Guide: v0.1.1 → v1.0.0

## Major Changes

### 1. Return Types Changed

**Before (v0.1.1):**
```python
result = procyl.create("worker", code)
# Returns: Dict[str, object]
```

**After (v1.0.0):**
```python
worker = procyl.create("worker", code)
# Returns: Worker object
# Type: procyl.Worker
```

### 2. New `.data` Property

Access worker metadata through the `.data` property:

```python
worker = procyl.create("demo", code)

# New properties:
worker.data.hash              # Code SHA256 hash
worker.data.compiler          # Compiler used
worker.data.compiled          # Is compiled?
worker.data.dependencies      # Set of external packages
worker.data.python_version    # Python version
worker.data.platform          # Platform (OS-Architecture)
worker.data.path              # Artifact path
worker.data.size              # Artifact size in bytes
worker.data.pid               # Current process ID
worker.data.running           # Is currently running?
```

### 3. New Environment Management: `procyl.prepare()`

**New in v1.0.0:**
```python
# Automatic dependency detection from all workers
procyl.prepare()

# With version constraints
procyl.prepare(constraints={
    "requests": "==2.32.3",
    "numpy": ">=2.3,<3"
})

# From requirements file
procyl.prepare(requirements="requirements.txt")
```

Creates isolated Python environment in `.procyl/env/`

### 4. New Methods

#### `worker.verify()`
```python
result = worker.verify()
# {
#     'name': 'worker_name',
#     'valid': True,
#     'issues': [],
#     'dependencies': ['requests', 'numpy'],
#     'compiled': False
# }
```

#### `worker.run(count=N)`
```python
# Run once
results = worker.run(count=1)

# Run 8 times in parallel
results = worker.run(count=8)

# With custom args
results = worker.run(count=4, args=["arg1", "arg2"])
# Returns: List[str]
```

### 5. Automatic Dependency Scanning

**New in v1.0.0** - All external dependencies are automatically detected:

```python
code = '''
import requests
import numpy as np
import os           # stdlib - ignored
import sys          # stdlib - ignored
'''

worker = procyl.create("demo", code)
print(worker.data.dependencies)
# Output: {'requests', 'numpy'}
```

## Migration Checklist

- [ ] Update `procyl.create()` calls - now returns `Worker` object, not dict
- [ ] Replace `.to_dict()` calls with `.data` property access
- [ ] Update code accessing worker properties - use `worker.data` for metadata
- [ ] Add `procyl.prepare()` call in initialization
- [ ] Remove manual dependency installation code
- [ ] Update tests to use new `.run()` method for parallel execution
- [ ] Use `.verify()` for worker validation instead of manual checks

## Backward Compatibility

The following v0.1.1 APIs still work:

- `procyl.run(name, args)` - unchanged
- `procyl.precompile(name, ...)` - still returns dict
- `procyl.runtime_compile(name, ...)` - still returns dict
- `procyl.status(name)` - still returns dict
- `procyl.delete(name)` - still returns dict

Only `procyl.create()` return type changed.

## Examples

### Before (v0.1.1)
```python
import procyl

worker_dict = procyl.create("app", code)
print(f"Worker: {worker_dict['name']}")
print(f"State: {worker_dict['state']}")

output = procyl.run("app", args=["hello"])
print(output)
```

### After (v1.0.0)
```python
import procyl

# Prepare environment once
procyl.prepare()

worker = procyl.create("app", code)
print(f"Worker: {worker.name}")
print(f"State: {worker.state}")
print(f"Dependencies: {worker.data.dependencies}")

# Single execution
output = procyl.run("app", args=["hello"])
print(output)

# Parallel execution
results = worker.run(count=4, args=["hello"])
for i, result in enumerate(results):
    print(f"Execution {i+1}: {result}")

# Verify worker
verification = worker.verify()
print(f"Valid: {verification['valid']}")
```

## Performance Notes

- Environment setup (`procyl.prepare()`) is a one-time operation
- Parallel execution uses `multiprocessing.Pool`
- Dependency detection uses AST analysis (very fast)
- Compiled artifacts are cached

## Troubleshooting

### "Worker not found" error
```python
# Correct:
worker = procyl.create("my_worker", code)
procyl.run("my_worker")

# NOT correct (outdated):
worker_dict = procyl.create("my_worker", code)
procyl.run("wrong_name")
```

### Missing `.data` property
```python
# This still works:
worker.to_dict()

# But also use:
worker.data.hash
worker.data.dependencies
# etc.
```

### Dependencies not detected
Ensure you use absolute imports:
```python
# ✓ Detected
import requests
from numpy import array

# ✗ Not detected (module-level imports only):
def my_func():
    import requests  # Function-level import - skipped
```
