$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
  py -3.10 -m venv .venv
}
& ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt
Write-Host "Checking API import..." -ForegroundColor Cyan
& ".\.venv\Scripts\python.exe" -c "import app.main; print('IMPORT_OK')"
Write-Host "Starting API at http://127.0.0.1:8000" -ForegroundColor Green
& ".\.venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
