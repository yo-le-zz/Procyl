#!/usr/bin/env python3
"""Quick verification script for procyl v1.0.0."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")
    try:
        import procyl
        from procyl import create, prepare, Worker
        from procyl.dependencies import get_dependencies_from_code
        from procyl.environment import get_environment
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False


def test_basic_worker():
    """Test basic worker creation."""
    print("\nTesting worker creation...")
    try:
        import procyl
        
        worker = procyl.create(
            "test",
            'print("Hello, v1.0.0!")'
        )
        
        assert isinstance(worker, procyl.Worker), "Worker is not Worker instance"
        assert worker.name == "test", "Worker name mismatch"
        assert hasattr(worker, "data"), "Worker missing .data property"
        
        print(f"✓ Worker created successfully")
        print(f"  - Hash: {worker.data.hash}")
        print(f"  - Compiler: {worker.data.compiler}")
        print(f"  - Platform: {worker.data.platform}")
        
        procyl.delete("test")
        return True
    except Exception as e:
        print(f"✗ Worker creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_dependency_detection():
    """Test dependency detection."""
    print("\nTesting dependency detection...")
    try:
        import procyl
        
        code = '''
import requests
import numpy
import os
print("test")
'''
        worker = procyl.create("dep_test", code)
        deps = worker.data.dependencies
        
        assert "requests" in deps, "requests not detected"
        assert "numpy" in deps, "numpy not detected"
        assert "os" not in deps, "stdlib module detected"
        
        print(f"✓ Dependency detection works")
        print(f"  - Found: {deps}")
        
        procyl.delete("dep_test")
        return True
    except Exception as e:
        print(f"✗ Dependency detection failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_worker_verify():
    """Test worker verification."""
    print("\nTesting worker verification...")
    try:
        import procyl
        
        worker = procyl.create("verify_test", 'print("ok")')
        result = worker.verify()
        
        assert result["valid"] is True, "Valid worker reported as invalid"
        assert "issues" in result, "Missing issues in result"
        
        print(f"✓ Worker verification works")
        print(f"  - Valid: {result['valid']}")
        print(f"  - Issues: {result['issues']}")
        
        procyl.delete("verify_test")
        return True
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("Procyl v1.0.0 - Quick Verification")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_basic_worker,
        test_dependency_detection,
        test_worker_verify,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    return all(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
