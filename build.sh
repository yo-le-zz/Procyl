#!/bin/bash

set -e

echo "== Procyl build =="

# dossiers
mkdir -p dist

echo "[1] Cleaning old build artifacts..."
rm -rf dist/
rm -rf build/
rm -rf *.egg-info

echo "[2] Removing Python cache..."
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

echo "[3] Building package..."
python -m build

echo "[4] Done."
echo "Output:"
ls -l dist/