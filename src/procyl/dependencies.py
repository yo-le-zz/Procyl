"""Scan and manage Python dependencies."""

from __future__ import annotations

import ast
import sys
from typing import Set, Optional, Dict, List, Tuple


# Get stdlib modules dynamically (Python 3.10+)
def _get_stdlib_modules() -> Set[str]:
    """Get standard library module names dynamically."""
    try:
        # Python 3.10+ has stdlib_module_names
        return set(sys.stdlib_module_names)  # type: ignore
    except AttributeError:
        # Fallback for older Python (shouldn't happen with >=3.10)
        return {
            "abc", "aifc", "argparse", "array", "ast", "asynchat", "asyncio",
            "asyncore", "atexit", "audioop", "base64", "bdb", "binascii", "binhex",
            "bisect", "builtins", "bz2", "calendar", "cgi", "cgitb", "chunk", "cmath",
            "cmd", "code", "codecs", "codeop", "collections", "colorsys", "compileall",
            "concurrent", "configparser", "contextlib", "contextvars", "copy", "copyreg",
            "cProfile", "crypt", "csv", "ctypes", "curses", "dataclasses", "datetime",
            "dbm", "decimal", "difflib", "dis", "distutils", "doctest", "dummy_thread",
            "dummy_threading", "email", "encodings", "ensurepip", "enum", "errno",
            "faulthandler", "fcntl", "filecmp", "fileinput", "fnmatch", "fractions",
            "ftplib", "functools", "gc", "getopt", "getpass", "gettext", "glob",
            "graphlib", "grp", "gzip", "hashlib", "heapq", "hmac", "html", "http",
            "idlelib", "imaplib", "imghdr", "imp", "importlib", "inspect", "io",
            "ipaddress", "itertools", "json", "keyword", "lib2to3", "linecache",
            "locale", "logging", "lzma", "mailbox", "mailcap", "marshal", "math",
            "mimetypes", "mmap", "modulefinder", "msilib", "msvcrt", "multiprocessing",
            "netrc", "nis", "nntplib", "numbers", "operator", "optparse", "os",
            "ossaudiodev", "parser", "pathlib", "pdb", "pickle", "pickletools", "pipes",
            "pkgutil", "platform", "plistlib", "poplib", "posix", "posixpath", "pprint",
            "profile", "pstats", "pty", "pwd", "py_compile", "pyclbr", "pydoc", "queue",
            "quopri", "random", "re", "readline", "reprlib", "resource", "rlcompleter",
            "runpy", "sched", "secrets", "select", "selectors", "shelve", "shlex",
            "shutil", "signal", "site", "smtpd", "smtplib", "sndhdr", "socket",
            "socketserver", "spwd", "sqlite3", "ssl", "stat", "statistics", "string",
            "stringprep", "struct", "subprocess", "sunau", "symbol", "symtable", "sys",
            "sysconfig", "syslog", "tabnanny", "tarfile", "telnetlib", "tempfile",
            "termios", "test", "textwrap", "threading", "time", "timeit", "tkinter",
            "token", "tokenize", "tomllib", "trace", "traceback", "tracemalloc", "tty",
            "turtle", "turtledemo", "types", "typing", "typing_extensions", "unicodedata",
            "unittest", "urllib", "uu", "uuid", "venv", "warnings", "wave", "weakref",
            "webbrowser", "winreg", "winsound", "wsgiref", "xdrlib", "xml", "xmlrpc",
            "zipapp", "zipfile", "zipimport", "zlib", "__future__",
        }


# Cache stdlib modules once
_STDLIB_MODULES: Optional[Set[str]] = None


def _get_cached_stdlib() -> Set[str]:
    """Get cached stdlib modules."""
    global _STDLIB_MODULES
    if _STDLIB_MODULES is None:
        _STDLIB_MODULES = _get_stdlib_modules()
    return _STDLIB_MODULES


class DependencyScanner:
    """Scan Python code for external dependencies.
    
    Thread-safe: uses no mutable state, all state is local to methods.
    """

    def scan_code(self, code: str) -> Set[str]:
        """Scan code for external dependencies.
        
        Args:
            code: Python code to scan
            
        Returns:
            Set of external package names (root module names)
        """
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return set()

        imports = self._extract_imports(tree)
        return self._filter_external(imports)

    def _extract_imports(self, tree: ast.AST) -> Set[str]:
        """Extract all imports from AST.
        
        Returns:
            Set of import names (root module only, e.g., 'tensorflow' from 'tensorflow.keras')
        """
        imports: Set[str] = set()
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # Handle: import X, import X.Y, import X as Y, import X.Y as Z
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    imports.add(root)
                    
            elif isinstance(node, ast.ImportFrom):
                # Skip relative imports (they're internal, not external deps)
                # node.level > 0 means it's a relative import (from . or from ..)
                if node.level > 0:
                    continue
                    
                # Handle absolute imports: from X import Y, from X.Y import Z
                if node.module:
                    root = node.module.split(".")[0]
                    imports.add(root)
        
        return imports

    @staticmethod
    def _filter_external(imports: Set[str]) -> Set[str]:
        """Filter out standard library modules.
        
        Args:
            imports: Set of module names
            
        Returns:
            Set of external (non-stdlib) module names
        """
        stdlib = _get_cached_stdlib()
        return {imp for imp in imports if imp not in stdlib and not imp.startswith("_")}


def get_dependencies_from_code(code: str) -> Set[str]:
    """Get external dependencies from Python code.
    
    Automatically detects:
    - import requests
    - from numpy import array
    - import tensorflow.keras
    - Relative imports (ignored)
    - Standard library modules (filtered)
    
    Args:
        code: Python code to analyze
        
    Returns:
        Set of external package names
    """
    scanner = DependencyScanner()
    return scanner.scan_code(code)


def parse_constraints(constraints: Optional[Dict[str, str]]) -> List[str]:
    """Parse constraint dictionary to pip format.
    
    Args:
        constraints: Dict like {"package": "==1.0.0", "numpy": ">=2.3,<3"}
                    None for empty constraints
        
    Returns:
        List of pip requirement strings
        
    Raises:
        ValueError: If constraint value is None or empty
    """
    if not constraints:
        return []
    
    requirements = []
    for name, version in constraints.items():
        if not name:
            raise ValueError("Package name cannot be empty")
        if version is None or version == "":
            raise ValueError(f"Package '{name}' has no version constraint")
        requirements.append(f"{name}{version}")
    
    return requirements


def read_requirements_file(path: str, encoding: str = "utf-8") -> List[str]:
    """Read requirements from a file.
    
    Handles:
    - UTF-8 encoding (configurable)
    - Comments (lines starting with #)
    - Empty lines
    - Windows/Unix line endings
    - Leading/trailing whitespace
    
    Args:
        path: Path to requirements.txt
        encoding: File encoding (default: utf-8)
        
    Returns:
        List of requirement strings
        
    Raises:
        FileNotFoundError: If file doesn't exist
        IOError: If file cannot be read
    """
    try:
        with open(path, encoding=encoding) as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        # Try with latin-1 as fallback
        with open(path, encoding="latin-1") as f:
            lines = f.readlines()
    
    requirements = []
    for line in lines:
        # Strip whitespace (handles \r\n on Windows, \n on Unix)
        line = line.strip()
        
        # Skip empty lines and comments
        if line and not line.startswith("#"):
            requirements.append(line)
    
    return requirements


def validate_requirement(requirement: str) -> Tuple[str, Optional[str]]:
    """Validate and parse a single requirement string.
    
    Args:
        requirement: Requirement string like "numpy>=1.20" or "requests"
        
    Returns:
        Tuple of (package_name, version_spec) where version_spec can be None
        
    Raises:
        ValueError: If requirement is invalid
    """
    if not requirement:
        raise ValueError("Requirement string cannot be empty")
    
    requirement = requirement.strip()
    
    # Find version operators
    operators = ["==", ">=", "<=", "!=", "~=", ">", "<"]
    package_name = requirement
    version_spec = None
    
    for op in operators:
        if op in requirement:
            parts = requirement.split(op, 1)
            package_name = parts[0].strip()
            version_spec = op + parts[1].strip()
            break
    
    if not package_name:
        raise ValueError("Package name cannot be empty")
    
    return package_name, version_spec

