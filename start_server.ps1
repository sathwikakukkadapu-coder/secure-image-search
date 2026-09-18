Set-Location $PSScriptRoot
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host " Starting Private Image Search Engine (SecureImage)  " -ForegroundColor Green
Write-Host " URL: http://localhost:8000/                        " -ForegroundColor Yellow
Write-Host "====================================================" -ForegroundColor Cyan
Start-Process "http://localhost:8000/"
& ".\.venv\Scripts\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
