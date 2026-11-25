# Recovery and startup verification

This delivery contains the backend entry point at:

    backend/app/main.py

Run commands from the `backend` directory (the directory containing `requirements.txt`),
not from `backend/app` and not from an older extracted copy.

PowerShell:

    cd <extracted-folder>\ai-software-bug-detective\backend
    py -3.10 -m venv .venv
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    .\.venv\Scripts\Activate.ps1
    python -m pip install -r requirements.txt
    python -c "import app.main; print('IMPORT_OK')"
    python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

If `Test-Path .\app\main.py` returns False, the terminal is in the wrong
extracted directory or the extraction is incomplete. Re-extract this ZIP into
a new, empty folder and repeat the commands. Do not copy only `__pycache__`
files; Python bytecode is not a replacement for source files.

Validation performed for this delivery:
- ZIP integrity check
- Backend Python compilation
- `import app.main`
- Backend automated tests: 34 passed, 1 skipped

Not verified in this environment:
- Your local PostgreSQL credentials/database and migrations
- Your machine's frontend production build
- Docker runtime execution
- Live Gemini API credentials/network access

The skipped test requires an optional AI provider SDK/service configuration.
