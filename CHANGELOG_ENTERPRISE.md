# Enterprise foundation update — 1.2.0

- Added safe multi-language static syntax/config analysis for Python, JavaScript/TypeScript, Java, PHP, Go and Ruby when local toolchains are available.
- Added heuristic security and performance signals with category, severity, file and line metadata.
- Extended finding analysis to preserve structured source line, severity and category.
- Added durable database-backed scan jobs, queue/status APIs and a separately run worker process.
- Added PostgreSQL SQL upgrade and Alembic revision for scan history/findings/queue.
- Added GitHub Actions CI template for backend tests and frontend build.
- Added end-to-end setup/test documentation and an explicit enterprise capability/limitations matrix.
- Backend suite in packaging environment: 33 passed, 1 skipped (Gemini SDK unavailable in this environment).
- Frontend build and live external integrations remain unverified.
