# Enterprise capabilities: implementation status

This delivery adds concrete foundations, but it is not a production-certified enterprise SaaS release.

| Area | Included in this delivery | Still required for production |
|---|---|---|
| Large repository processing | ZIP limits, ignored dependency/build folders, 1 MB per-file analysis cap, durable DB-backed scan queue and separate worker process | Redis/Celery or equivalent distributed queue, object storage, horizontal workers, resumable chunk indexing and load testing |
| Multi-language analysis | Safe syntax/config checks for Python, JavaScript/TypeScript, Java, PHP, Go and Ruby when their local parser/compiler is installed; JSON/XML/YAML checks; heuristic security/performance signals | Language-specific SAST engines, dependency/SBOM scanners, framework-aware dataflow analysis, validated rule packs |
| AI diagnosis | Existing provider-based AI diagnosis and RAG foundations; cautious confidence and suggested fix output | Live provider credentials, evaluation dataset, prompt-injection hardening, human approval and patch verification |
| Test execution | Existing isolated Docker Python/pytest runner; safe static fallback when Docker/image is missing | Dedicated reviewed images and runners for Node, Java, .NET, Go, PHP; test dependency allowlists; execution queue and artifact retention |
| Security/performance | Static heuristic checks for likely hard-coded secrets, eval, shell execution, disabled TLS verification, possible N+1 queries and unbounded reads | Full SAST/DAST, secret scanning with entropy/context, dependency CVE checks, load tests, threat model and penetration test |
| GitHub / CI/CD | GitHub Actions workflow template runs backend tests and frontend build on push/PR | GitHub App/OAuth installation, repository selection, webhook ingestion, status checks and secure token lifecycle |
| Team / company isolation | Existing owner checks and role-based access in API | Organization/tenant schema, invitations, per-tenant role matrix, tenant-scoped queries, audit log, retention policy and isolation tests |
| Reporting | Persisted scan history/findings, PDF and Excel reporting | Signed immutable reports, scheduled delivery, audit trail and report retention controls |

## Important safety note

The static analyzer reads and parses uploaded files. It does not run uploaded application code. Runtime tests are only attempted through the configured Docker runner. A static finding is a review signal, not proof of exploitability or a guaranteed defect.
