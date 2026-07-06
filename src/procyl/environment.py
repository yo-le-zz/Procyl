"""Manage Python environment for workers."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import venv
from pathlib import Path
from typing import Optional, Dict, List, Set

from .dependencies import (
    get_dependencies_from_code,
    parse_constraints,
    read_requirements_file,
)


class Environment:
    """Manage isolated Python environment for workers."""

    PROCYL_ENV_DIR = ".procyl"
    ENV_NAME = "env"
    METADATA_FILE = "metadata.json"

    def __init__(self, base_path: Optional[str] = None):
        """Initialize environment manager.
        
        Args:
            base_path: Base directory for environment (default: current dir/.procyl)
        """
        if base_path is None:
            base_path = os.path.join(os.getcwd(), self.PROCYL_ENV_DIR)
        
        self.base_path = Path(base_path)
        self.env_path = self.base_path / self.ENV_NAME
        self.metadata_path = self.base_path / self.METADATA_FILE
        self.is_prepared = self._check_prepared()

    def _check_prepared(self) -> bool:
        """Check if environment is already prepared."""
        return self.env_path.exists() and self.metadata_path.exists()

    def get_python_executable(self) -> str:
        """Get path to python executable in venv."""
        if sys.platform == "win32":
            return str(self.env_path / "Scripts" / "python.exe")
        return str(self.env_path / "bin" / "python")

    def get_pip_executable(self) -> str:
        """Get path to pip executable in venv."""
        if sys.platform == "win32":
            return str(self.env_path / "Scripts" / "pip.exe")
        return str(self.env_path / "bin" / "pip")

    def prepare(
        self,
        dependencies: Optional[Set[str]] = None,
        constraints: Optional[Dict[str, str]] = None,
        requirements_file: Optional[str] = None,
    ) -> bool:
        """Prepare the environment.
        
        Args:
            dependencies: Set of package names to install
            constraints: Dict of package==version constraints
            requirements_file: Path to requirements.txt
            
        Returns:
            True if successful
        """
        if self.is_prepared:
            return True

        # Create base directory
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create venv
        print(f"Creating virtual environment at {self.env_path}...")
        venv.create(str(self.env_path), with_pip=True)

        # Prepare installation list
        install_list = []

        if requirements_file and os.path.exists(requirements_file):
            print(f"Reading requirements from {requirements_file}...")
            install_list.extend(read_requirements_file(requirements_file))
        else:
            if dependencies:
                install_list.extend(sorted(dependencies))
            if constraints:
                install_list.extend(parse_constraints(constraints))

        # Install dependencies
        if install_list:
            print(f"Installing {len(install_list)} dependencies...")
            pip_exe = self.get_pip_executable()
            try:
                result = subprocess.run(
                    [pip_exe, "install", "-q"] + install_list,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if result.returncode != 0:
                    print(f"Installation error: {result.stderr}")
                    return False
            except subprocess.TimeoutExpired:
                print("Installation timed out")
                return False
        
        # Save metadata
        metadata = {
            "python_version": sys.version,
            "platform": sys.platform,
            "dependencies": sorted(dependencies or []),
            "constraints": constraints or {},
        }
        with open(self.metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        self.is_prepared = True
        print(f"Environment ready at {self.env_path}")
        return True

    def cleanup(self) -> bool:
        """Remove the environment."""
        if self.env_path.exists():
            shutil.rmtree(self.env_path)
        if self.metadata_path.exists():
            self.metadata_path.unlink()
        self.is_prepared = False
        return True

    def get_metadata(self) -> Optional[Dict]:
        """Get environment metadata."""
        if not self.metadata_path.exists():
            return None
        with open(self.metadata_path) as f:
            return json.load(f)


# Global environment instance
_env: Optional[Environment] = None


def get_environment(base_path: Optional[str] = None) -> Environment:
    """Get or create global environment instance."""
    global _env
    if _env is None:
        _env = Environment(base_path)
    return _env
