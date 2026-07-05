@echo off
setlocal

echo == Procyl build ==

echo [1] Cleaning old build artifacts...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build

for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q *.pyc >nul 2>&1

echo [2] Building package...
python -m build

echo [3] Done.
dir dist

endlocal
pause