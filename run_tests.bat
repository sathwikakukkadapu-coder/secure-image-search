@echo off
cd /d "%~dp0"
.\.venv\Scripts\python.exe tests\test_system.py
pause
