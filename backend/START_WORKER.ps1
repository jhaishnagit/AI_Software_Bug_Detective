$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".\.venv\Scripts\python.exe")) { throw "Backend virtual environment not found. Start the backend setup first." }
Write-Host "Starting background scan worker. Keep this terminal open." -ForegroundColor Green
& ".\.venv\Scripts\python.exe" -m app.worker
