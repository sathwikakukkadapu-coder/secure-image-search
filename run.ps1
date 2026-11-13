Set-Location -Path $PSScriptRoot
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Starting SecureImage Live Platform on http://localhost:8000" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

if (Test-Path ".\.venv\Scripts\python.exe") {
    Write-Host "Using project virtual environment (.venv)..." -ForegroundColor Yellow
    & ".\.venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
} else {
    Write-Host "Using system python..." -ForegroundColor Yellow
    python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
}
