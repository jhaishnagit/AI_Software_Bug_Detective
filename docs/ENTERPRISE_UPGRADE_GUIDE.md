# AI Software Bug Detective — Enterprise Foundation Update

## What changed in this delivery

This update is built on the supplied application source and PostgreSQL backup. It is an incremental foundation update, not a claim that every enterprise capability is complete or production-certified.

### Implemented in this update

- Align SQLAlchemy mappings with the supplied PostgreSQL schema:
  - `project_uploads.project_id`
  - `test_cases.project_id`, `test_cases.upload_id`, `test_cases.source_key`, nullable `test_cases.bug_id`
  - Existing `test_execution_history` table
- Persist each static source scan in `scan_runs`.
- Convert failed static syntax/manifest checks into durable Bug Tracker records.
- Deduplicate repeat findings for the same uploaded archive with `scan_findings` fingerprints.
- Persist AI-generated project test cases in `test_cases` and return their database IDs.
- Persist isolated test-runner outcomes in `test_execution_history`.
- Add scan history and execution history APIs.
- Add a Scan Reports screen and PDF export alongside the existing Excel export.
- Keep the existing safety behavior: uploaded source code is parsed/static-checked; runtime tests are only run through the configured Docker runner. Without Docker, the runner reports static fallback and does not execute uploaded code on the host.

## Existing database tables from the supplied backup

The supplied `backup.sql` contains these 10 tables:

1. `users`
2. `projects`
3. `project_uploads`
4. `source_chunks`
5. `bugs`
6. `bug_analysis`
7. `bug_attachments`
8. `test_cases`
9. `test_execution_history`
10. `alembic_version`

This update adds two tables:

11. `scan_runs`
12. `scan_findings`

No existing data is intentionally deleted or rewritten by `01_enterprise_upgrade.sql`.

## Database update steps (PostgreSQL / pgAdmin)

1. Take a fresh backup of the database you currently use.
2. Open pgAdmin → select the existing project database → Query Tool.
3. Open and execute `database/01_enterprise_upgrade.sql` once.
4. Check that `scan_runs` and `scan_findings` appear under Schemas → public → Tables.
5. Run the verification queries at the bottom of the SQL file.
6. Configure `DATABASE_URL` in `backend/.env` to point to this same database.

`database/00_existing_schema_reference.sql` is a schema-only reference extracted from the supplied backup. It is intended for a clean database/schema review. Do not run it over a populated database; use the additive upgrade script above for the existing database.

## Backend setup

From `backend/` in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Set at least these local `.env` values (replace the placeholders):

```env
DATABASE_URL=postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/bug_detective
JWT_SECRET=REPLACE_WITH_A_LONG_RANDOM_SECRET
AI_PROVIDER=mock
```

Then start:

```powershell
python -m uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs

## Frontend setup

From `frontend/` in a second PowerShell terminal:

```powershell
npm install
Copy-Item .env.example .env
npm run dev
```

The default frontend URL is normally http://localhost:5173.

## New / updated API endpoints

- `POST /api/projects/{upload_id}/run-tests` — static scan; stores scan run and detected findings.
- `GET /api/scan-runs?limit=50&offset=0` — recent scan history for the authenticated user's projects (ADMIN/MANAGER can see all current projects).
- `GET /api/projects/{upload_id}/scan-history` — scan history for an owned upload.
- `GET /api/projects/{upload_id}/execution-history` — runtime/static fallback execution history.
- `GET /api/projects/{upload_id}/test-report/pdf` — formatted PDF report.
- `GET /api/projects/{upload_id}/test-report/excel` — existing Excel report, now based on the latest persisted scan.
- `POST /api/projects/{upload_id}/generate-test-cases` — generated project-level test cases are persisted and include database IDs.

## Current limits and important distinctions

- ZIP upload validation allows up to 500 MB compressed, 200 MB uncompressed, and 5,000 files.
- The current runtime execution endpoint has a stricter 100 MB uncompressed limit.
- Static scanning currently checks supported Python/JavaScript/TypeScript syntax and `package.json` manifest validity. It is not a full semantic bug detector and cannot find every business-logic defect.
- Project test-case generation sends a bounded sample of source files to the configured AI provider. It does not mean every file in a very large repository is deeply understood by the model.
- Generated test cases are proposals until an appropriate runner executes them.
- The Docker runner currently runs Python `pytest` tests from a `tests/` directory. It is not yet a universal runner for Java, Node, .NET, Go, etc.
- Performance testing, comprehensive security scanning, multi-tenant company isolation, GitHub/CI integration, distributed job queues, and enterprise-grade monitoring are not completed by this update.
- Configure a real AI provider key to use live AI. `AI_PROVIDER=mock` is clearly labeled heuristic output.

## Security notes

- Never copy the original `.env` files or API keys into the delivered ZIP.
- Use a strong JWT secret and restrict CORS before deployment.
- Keep uploaded code in controlled storage. Do not execute untrusted source on the API host.
- The current Docker runner has resource restrictions, but production deployment still needs hardened container images, malware scanning, storage quotas, job isolation, and operational monitoring.
- Review AI provider data handling before sending private source code to an external provider.

## Verification status

The delivered code was syntax-checked during packaging. Full PostgreSQL integration tests, browser-based end-to-end tests, Docker image validation, and a live external AI-provider test were not performed in this packaging environment. Run the backend tests and frontend build in your local project environment before using it with your existing database.
