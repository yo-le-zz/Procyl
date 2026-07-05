import subprocess
import tempfile
import os

def run_code(code: str):
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name

    try:
        result = subprocess.run(
            ["python", path],
            capture_output=True,
            text=True
        )
        return result.stdout + result.stderr
    finally:
        os.remove(path)