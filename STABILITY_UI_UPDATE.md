# AI Software Bug Detective — Stability & UI Update

## What changed
- Frontend API timeout increased from 30 seconds to 120 seconds for slower analysis/report calls.
- Clear frontend diagnostics for backend connection-refused and request-timeout errors.
- If `AI_PROVIDER=gemini` but `GEMINI_API_KEY` is empty, test-case generation now uses the clearly labelled heuristic/mock fallback instead of failing with a 502. This is NOT Gemini/LLM output.
- Refined responsive UI palette: midnight navy navigation, clean light workspace, indigo-to-blue actions, teal status accents, clearer cards and forms.
- Added Windows PowerShell startup scripts for API and background worker.

## Start on Windows

### 1. Backend API (Terminal 1)
Open PowerShell in this `backend` folder and run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\START_BACKEND.ps1
```

Keep this terminal open. Check the API in your browser:
`http://127.0.0.1:8000/api/health`

It should return JSON with `status: ok`.

### 2. Background scan worker (Terminal 2)
Open a second PowerShell in this same `backend` folder and run:

```powershell
.\START_WORKER.ps1
```

Keep this terminal open while background scans are queued.

### 3. Frontend (Terminal 3)
From the `frontend` folder:

```powershell
npm ci
npm run dev
```

Open the Vite URL shown in the terminal (normally `http://localhost:5173`).

## AI configuration
For a working no-key development mode, set in `backend/.env`:

```env
AI_PROVIDER=mock
GEMINI_API_KEY=
```

This provides heuristic suggestions and clearly identifies itself as mock/heuristic output. It is not generative AI.

To enable Gemini:
```env
AI_PROVIDER=gemini
GEMINI_API_KEY=PASTE_YOUR_VALID_GEMINI_API_KEY_HERE
GEMINI_MODEL=gemini-3.6-flash
```
Restart the backend after changing `.env`. Never commit `.env` or share API keys.

## Database
Keep your existing PostgreSQL `DATABASE_URL` if your database is running and the schema is compatible. Do not delete the database or run destructive reset commands. The API will not start if PostgreSQL is stopped, credentials are invalid, or schema initialization fails. Check the backend terminal traceback first.

The database password was included in the chat message. Rotate it before using this project outside local development, then update `DATABASE_URL` in `.env`.

## Recommended workflow
1. Start PostgreSQL.
2. Start backend API and verify `/api/health`.
3. Start worker in a separate terminal.
4. Start frontend.
5. Upload a clean ZIP.
6. Analyze source.
7. Generate test cases.
8. Queue background scan and refresh its status.
9. Review Bugs, Test Cases, and Scan Reports.

## Important limitations
- Static checks and heuristic findings are not a complete SAST/DAST security audit.
- The worker is a single-process database-backed worker, not a distributed queue.
- Uploaded source is inspected in a temporary directory and is not run by static scanning. Runtime execution must remain isolated in a properly configured sandbox.
- Real Gemini analysis requires a valid API key and network/quota availability.
