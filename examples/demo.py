"""Procyl v1.0.0 Demo - Comprehensive example of all features."""

import procyl

# ============================================================================
# 1. Create workers with automatic dependency detection
# ============================================================================

print("=" * 70)
print("1. Creating workers (dependencies detected automatically)")
print("=" * 70)

# Simple worker - no external dependencies
hello_worker = procyl.create(
    "hello",
    '''
import sys
print("Hello from Procyl!")
print(f"Arguments: {sys.argv[1:]}")
''',
)
print(f"✓ Created worker: {hello_worker.name}")

# Worker with external dependencies
requests_worker = procyl.create(
    "requests_demo",
    '''
import requests
print("requests module imported successfully")
print(f"requests version: {requests.__version__}")
''',
)
print(f"✓ Created worker: {requests_worker.name}")

# ============================================================================
# 2. Inspect worker data (.data property)
# ============================================================================

print("\n" + "=" * 70)
print("2. Inspecting worker metadata")
print("=" * 70)

print(f"\nWorker: {hello_worker.name}")
print(f"  Hash: {hello_worker.data.hash}")
print(f"  Compiler: {hello_worker.data.compiler}")
print(f"  Compiled: {hello_worker.data.compiled}")
print(f"  Python: {hello_worker.data.python_version}")
print(f"  Platform: {hello_worker.data.platform}")
print(f"  Dependencies: {hello_worker.data.dependencies}")

# ============================================================================
# 3. Verify workers
# ============================================================================

print("\n" + "=" * 70)
print("3. Verifying worker integrity")
print("=" * 70)

verification = hello_worker.verify()
print(f"\nVerification for '{hello_worker.name}':")
print(f"  Valid: {verification['valid']}")
if verification['issues']:
    for issue in verification['issues']:
        print(f"  Issue: {issue}")

# ============================================================================
# 4. Prepare environment with dependencies
# ============================================================================

print("\n" + "=" * 70)
print("4. Preparing Python environment")
print("=" * 70)

print("\nPreparing environment with specific constraints...")
success = procyl.prepare(
    constraints={
        "requests": ">=2.28.0",  # Specify requests
    }
)

if success:
    print("✓ Environment prepared successfully!")
else:
    print("✗ Failed to prepare environment")

# ============================================================================
# 5. Run workers
# ============================================================================

print("\n" + "=" * 70)
print("5. Running workers")
print("=" * 70)

# Run single execution
print("\nRunning hello_worker once:")
output = procyl.run("hello", args=["--demo", "arg2"])
print(output)

# Run worker multiple times in parallel
print("\nRunning hello_worker 3 times in parallel:")
results = hello_worker.run(count=3, args=["test"])
for i, result in enumerate(results, 1):
    print(f"  Execution {i}:")
    print(f"    {result.strip()}")

# ============================================================================
# 6. Check worker status
# ============================================================================

print("\n" + "=" * 70)
print("6. Checking worker status")
print("=" * 70)

status = procyl.status("hello")
print(f"\nStatus of '{hello_worker.name}':")
print(f"  Name: {status['name']}")
print(f"  State: {status['state']}")
print(f"  Compiled: {bool(status.get('artifact_path'))}")

# ============================================================================
# 7. Cleanup
# ============================================================================

print("\n" + "=" * 70)
print("7. Cleanup")
print("=" * 70)

result = procyl.delete("hello")
print(f"\nDeleted '{result['name']}': {result['deleted']}")

result = procyl.delete("requests_demo")
print(f"Deleted 'requests_demo': {result['deleted']}")

print("\n" + "=" * 70)
print("Demo completed!")
print("=" * 70)
