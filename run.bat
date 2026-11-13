@echo off
title SecureImage Live Server
echo ========================================================
echo  Starting SecureImage Platform on http://localhost:8000
echo ========================================================
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    echo Using project virtual environment (.venv)...
    ".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
) else (
    echo Virtual environment not found, falling back to system python...
    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
)
pause
