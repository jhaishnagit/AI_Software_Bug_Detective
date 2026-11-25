# AI Software Bug Detective — Full source delivery

This is a source-code delivery based on the complete application folder in the latest uploaded archive. It includes the previous scan/report persistence work plus additional safe static-analysis and background-queue foundations. It is **not** a production-certified enterprise SaaS release.

## Implemented in this delivery

1. Persisted scan runs in `scan_runs`.
2. Failed supported checks create Bug Tracker records.
3. Repeated findings are deduplicated by a stable fingerprint in `scan_findings`.
4. Project-level AI-generated test cases are persisted in `test_cases`.
5. Test execution outcomes are persisted in `test_execution_history`.
6. Scan history and execution history APIs.
7. Scan Reports frontend view, PDF and Excel report endpoints.
8. Database-backed scan queue: `scan_jobs`, `POST /api/projects/{upload_id}/scan-jobs`, `GET /api/scan-jobs/{job_id}`, and a separately run worker (`python -m app.worker`).
9. Safe static syntax/config checks for Python, JavaScript/TypeScript, Java, PHP, Go and Ruby when the corresponding parser/compiler is installed; JSON/XML checks and optional YAML parsing.
10. Heuristic security signals for possible hard-coded credentials, private keys, dynamic `eval`, shell execution and disabled TLS verification.
11. Heuristic performance signals for possible database N+1 patterns and unbounded reads.
12. GitHub Actions workflow template for backend tests and frontend production build on push/PR.
13. Gemini SDK optional import for mock/OpenAI/Groq modes; clear setup error when Gemini mode is selected without the SDK.
14. Additive PostgreSQL upgrade SQL and an Alembic revision for scan history/queue tables.
15. Setup, validation and enterprise-limit documentation.

## Verification performed in this packaging environment

- Python compile check: passed.
- Backend automated tests: **33 passed, 1 skipped**.
- The skipped module requires `google-genai`; package installation could not be completed here because external package registry access was unavailable. `google-genai` remains in `backend/requirements.txt`; install requirements on the target machine to run the Gemini-specific tests.
- Frontend production build: **not verified**. `npm ci` could not complete in this environment. The package uses Babel parser 8 which requires Node 22.18+ (Node 24/26 is suitable); use a supported Node version on the target machine.
- Live PostgreSQL migration/connectivity, real Gemini calls, Docker runtime tests, and GitHub workflow execution were not performed here.

## Still not implemented / requires a separate production phase

- Distributed queue (Redis/Celery), horizontal workers, resumable chunked processing and load testing. The included DB-backed queue is a single-worker foundation.
- Full organization/company multi-tenancy, invitations, tenant-scoped RBAC, audit logs and retention policies. Current owner/role authorization is not a complete multi-company security boundary.
- Dedicated isolated runtime images for Node, Java, .NET, Go, PHP, Ruby, etc. Current Docker runtime runner remains Python/pytest only.
- Full SAST/DAST, dependency CVE/SBOM scans, validated secret scanning, performance/load testing and penetration testing. The included security/performance checks are heuristics and can produce false positives/negatives.
- GitHub App/OAuth, repository import, webhook ingestion, PR annotations and CI status-check integration. The included workflow is a CI template only.
- AI-generated fixes are suggestions, not verified patches. Human review and regression testing remain required.

## Before use

1. Back up the existing project folder and PostgreSQL database.
2. Extract this package into a new folder; do not overwrite the existing working project.
3. Create local `.env` files from `.env.example`; this package intentionally excludes actual secrets.
4. Follow `docs/LOCAL_SETUP_AND_VALIDATION.md` step by step.
5. For an existing PostgreSQL database, run `database/01_enterprise_upgrade.sql` once after backup. Do not also apply the equivalent Alembic revision to the same tables.
6. Run backend tests and frontend build locally before manager submission.
