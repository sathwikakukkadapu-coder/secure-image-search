@echo off
title Private Image Search - SecureImage
echo ====================================================
echo Starting Private Image Search Engine...
echo ====================================================
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo [Setup] Creating virtual environment...
    "C:\Users\Sathwika\.local\bin\uv.exe" venv .venv --python 3.12
    echo [Setup] Installing dependencies...
    "C:\Users\Sathwika\.local\bin\uv.exe" pip install -r requirements.txt --python .venv\Scripts\python.exe
)
echo Server starting at http://localhost:8000/
start http://localhost:8000/
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
pause
