# Local setup and end-to-end validation (Windows PowerShell)

## 1. Keep your current project safe

1. Stop the old backend and frontend terminals.
2. Take a copy of your current project folder and database backup.
3. Extract this ZIP into a new folder. Do not overwrite the old folder.
4. Create local `.env` files from the provided `.env.example` files. Never commit `.env` or share API/database secrets.

## 2. Backend setup

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `backend/.env` with your PostgreSQL connection string and a strong random `JWT_SECRET`. For local smoke testing only, SQLite can be used. Keep `AI_PROVIDER=mock` until the API flow works; configure `GEMINI_API_KEY` only when you want to test live Gemini.

For a fresh local database, start the API once so SQLAlchemy creates supported tables. For an existing PostgreSQL database, back it up first and run `database/01_enterprise_upgrade.sql` in pgAdmin/psql. Verify `scan_runs`, `scan_findings`, and `scan_jobs` exist. Do not drop existing tables.

Start the API:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs`. Check `GET /api/health` returns status `ok`.

## 3. Frontend setup

Open a second PowerShell terminal:

```powershell
cd frontend
npm ci
Copy-Item .env.example .env
npm run dev
```

Open the Vite URL printed in the terminal (normally `http://localhost:5173`). Register a test account, sign in, create a project and upload a small ZIP containing source code.

## 4. Test the synchronous scan flow

1. In the application, upload a ZIP with at least one `.py` or `.js` file and a `package.json` if applicable.
2. Run the source/static checks.
3. Confirm the response has `total_checks`, `passed`, `failed`, `skipped`, `languages_detected` and `results`.
4. Add a deliberately invalid Python file (for example `def broken(:`) to a separate test ZIP and scan it. A syntax finding should appear.
5. Open Bug Management. Confirm the finding was persisted as a bug.
6. Open Scan Reports. Confirm the scan history is present and try PDF/Excel export.
7. Run test execution. If Docker and the configured runner image are unavailable, the response must clearly say runtime tests were not executed and static fallback was used.

## 5. Test the background scan queue

Keep the API terminal running. Open another terminal:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
python -m app.worker
```

Use Swagger or an authenticated API client:

- `POST /api/projects/{upload_id}/scan-jobs` queues a scan and returns `job_id`.
- Poll `GET /api/scan-jobs/{job_id}` until `COMPLETED` or `FAILED`.

The worker must stay running separately from Uvicorn. If it is not running, jobs remain `QUEUED`.

## 6. Run automated tests and build

Backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH = "."
pytest -q tests
```

Frontend:

```powershell
cd frontend
npm ci
npm run build
```

## 7. GitHub Actions

The included `.github/workflows/bug-detective-ci.yml` is a CI template. Commit and push it to a GitHub repository to run backend tests and frontend build on pushes and pull requests. This is not a GitHub App integration and does not automatically import repositories into the product.

## 8. Go/no-go checklist

Do not submit as fully working until all applicable items pass in your own environment:

- [ ] Backend starts without traceback.
- [ ] Frontend `npm run build` succeeds.
- [ ] PostgreSQL health/connectivity verified (not just API process startup).
- [ ] Register/login and protected API calls work.
- [ ] Upload a project ZIP and scan it.
- [ ] A known syntax issue appears in Bug Management.
- [ ] Scan history and PDF/Excel reports work.
- [ ] Background worker processes a queued job.
- [ ] Docker runtime test behavior is correctly reported.
- [ ] Existing production data remains intact after migration.

Do not send `.env`, API keys, JWT secrets, database passwords, or uploaded customer source code in a public repository.
