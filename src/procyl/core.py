from .runner import run_code

_workers = {}

def create(name: str, code: str):
    _workers[name] = code

def run(name: str):
    if name not in _workers:
        raise ValueError(f"Worker '{name}' not found")
    return run_code(_workers[name])

def status(name: str):
    return "exists" if name in _workers else "missing"

def delete(name: str):
    _workers.pop(name, None)