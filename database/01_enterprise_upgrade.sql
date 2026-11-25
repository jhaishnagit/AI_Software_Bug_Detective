-- AI Software Bug Detective: Enterprise scan persistence upgrade
-- Run this once against the EXISTING project database after taking a backup.
-- The supplied database already contains 10 core tables, including
-- test_execution_history. This script adds only the two scan-history tables.

BEGIN;

CREATE TABLE IF NOT EXISTS public.scan_runs (
    id SERIAL PRIMARY KEY,
    upload_id VARCHAR(32) NOT NULL REFERENCES public.project_uploads(upload_id),
    project_id INTEGER NOT NULL REFERENCES public.projects(id),
    initiated_by INTEGER NOT NULL REFERENCES public.users(id),
    status VARCHAR(40) NOT NULL,
    execution_mode VARCHAR(40) NOT NULL DEFAULT 'STATIC_SAFE_CHECKS',
    total_checks INTEGER NOT NULL DEFAULT 0,
    passed INTEGER NOT NULL DEFAULT 0,
    failed INTEGER NOT NULL DEFAULT 0,
    errors INTEGER NOT NULL DEFAULT 0,
    skipped INTEGER NOT NULL DEFAULT 0,
    files_checked INTEGER NOT NULL DEFAULT 0,
    duration_seconds DOUBLE PRECISION NOT NULL DEFAULT 0,
    summary JSON NOT NULL DEFAULT '{}'::json,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_scan_runs_upload_id
    ON public.scan_runs USING btree (upload_id);
CREATE INDEX IF NOT EXISTS ix_scan_runs_project_id
    ON public.scan_runs USING btree (project_id);
CREATE INDEX IF NOT EXISTS ix_scan_runs_initiated_by
    ON public.scan_runs USING btree (initiated_by);
CREATE INDEX IF NOT EXISTS ix_scan_runs_project_created
    ON public.scan_runs USING btree (project_id, created_at);

CREATE TABLE IF NOT EXISTS public.scan_findings (
    id SERIAL PRIMARY KEY,
    upload_id VARCHAR(32) NOT NULL REFERENCES public.project_uploads(upload_id),
    project_id INTEGER NOT NULL REFERENCES public.projects(id),
    scan_run_id INTEGER NOT NULL REFERENCES public.scan_runs(id),
    bug_id INTEGER NOT NULL REFERENCES public.bugs(id),
    fingerprint VARCHAR(64) NOT NULL,
    rule_code VARCHAR(80) NOT NULL DEFAULT 'STATIC_CHECK',
    source_file VARCHAR(512) NOT NULL DEFAULT '',
    line_number INTEGER,
    severity VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    finding_status VARCHAR(30) NOT NULL DEFAULT 'OPEN',
    title VARCHAR(220) NOT NULL,
    details TEXT NOT NULL DEFAULT '',
    root_cause TEXT NOT NULL DEFAULT '',
    suggested_fix TEXT NOT NULL DEFAULT '',
    first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    occurrence_count INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uq_scan_findings_upload_fingerprint UNIQUE (upload_id, fingerprint)
);

CREATE INDEX IF NOT EXISTS ix_scan_findings_upload_id
    ON public.scan_findings USING btree (upload_id);
CREATE INDEX IF NOT EXISTS ix_scan_findings_project_id
    ON public.scan_findings USING btree (project_id);
CREATE INDEX IF NOT EXISTS ix_scan_findings_scan_run_id
    ON public.scan_findings USING btree (scan_run_id);
CREATE INDEX IF NOT EXISTS ix_scan_findings_bug_id
    ON public.scan_findings USING btree (bug_id);
CREATE INDEX IF NOT EXISTS ix_scan_findings_project_severity
    ON public.scan_findings USING btree (project_id, severity);



-- Durable scan queue used by backend/app/worker.py.
CREATE TABLE IF NOT EXISTS public.scan_jobs (
    id VARCHAR(32) PRIMARY KEY,
    upload_id VARCHAR(32) NOT NULL REFERENCES public.project_uploads(upload_id),
    owner_id INTEGER NOT NULL REFERENCES public.users(id),
    status VARCHAR(24) NOT NULL DEFAULT 'QUEUED',
    progress INTEGER NOT NULL DEFAULT 0,
    result JSON NOT NULL DEFAULT '{}'::json,
    error_message TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE NULL,
    completed_at TIMESTAMP WITH TIME ZONE NULL
);
CREATE INDEX IF NOT EXISTS ix_scan_jobs_status_created ON public.scan_jobs(status, created_at);
CREATE INDEX IF NOT EXISTS ix_scan_jobs_upload_id ON public.scan_jobs(upload_id);
CREATE INDEX IF NOT EXISTS ix_scan_jobs_owner_id ON public.scan_jobs(owner_id);

-- These columns already exist in the supplied backup. This block validates
-- them so a different/older database is not silently treated as compatible.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='project_uploads' AND column_name='project_id'
    ) THEN
        RAISE EXCEPTION 'Missing project_uploads.project_id. Review the database migration before continuing.';
    END IF;
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema='public' AND table_name='test_cases' AND column_name='upload_id'
    ) THEN
        RAISE EXCEPTION 'Missing test_cases.upload_id. Review the database migration before continuing.';
    END IF;
    IF to_regclass('public.test_execution_history') IS NULL THEN
        RAISE EXCEPTION 'Missing test_execution_history table. Restore/upgrade the supplied core schema first.';
    END IF;
END $$;

COMMIT;

-- Verification queries
SELECT table_name
FROM information_schema.tables
WHERE table_schema='public'
  AND table_name IN ('users','projects','project_uploads','source_chunks','bugs',
                     'bug_analysis','bug_attachments','test_cases',
                     'test_execution_history','scan_runs','scan_findings','scan_jobs','alembic_version')
ORDER BY table_name;

SELECT COUNT(*) AS scan_runs_count FROM public.scan_runs;
SELECT COUNT(*) AS scan_findings_count FROM public.scan_findings;

SELECT COUNT(*) AS scan_jobs_count FROM public.scan_jobs;
