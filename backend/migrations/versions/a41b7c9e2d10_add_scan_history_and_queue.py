"""Add persistent scan history, findings and background queue."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a41b7c9e2d10"
down_revision: Union[str, Sequence[str], None] = "9d7e2f1c4a60"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "scan_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("upload_id", sa.String(length=32), sa.ForeignKey("project_uploads.upload_id"), nullable=False),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("initiated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("execution_mode", sa.String(length=40), nullable=False, server_default="STATIC_SAFE_CHECKS"),
        sa.Column("total_checks", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("passed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("failed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("errors", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("files_checked", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_seconds", sa.Float(), nullable=False, server_default="0"),
        sa.Column("summary", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_scan_runs_upload_id", "scan_runs", ["upload_id"])
    op.create_index("ix_scan_runs_project_id", "scan_runs", ["project_id"])
    op.create_index("ix_scan_runs_initiated_by", "scan_runs", ["initiated_by"])
    op.create_index("ix_scan_runs_project_created", "scan_runs", ["project_id", "created_at"])

    op.create_table(
        "scan_findings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("upload_id", sa.String(length=32), sa.ForeignKey("project_uploads.upload_id"), nullable=False),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=False),
        sa.Column("scan_run_id", sa.Integer(), sa.ForeignKey("scan_runs.id"), nullable=False),
        sa.Column("bug_id", sa.Integer(), sa.ForeignKey("bugs.id"), nullable=False),
        sa.Column("fingerprint", sa.String(length=64), nullable=False),
        sa.Column("rule_code", sa.String(length=80), nullable=False, server_default="STATIC_CHECK"),
        sa.Column("source_file", sa.String(length=512), nullable=False, server_default=""),
        sa.Column("line_number", sa.Integer(), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("finding_status", sa.String(length=30), nullable=False, server_default="OPEN"),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("details", sa.Text(), nullable=False, server_default=""),
        sa.Column("root_cause", sa.Text(), nullable=False, server_default=""),
        sa.Column("suggested_fix", sa.Text(), nullable=False, server_default=""),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("occurrence_count", sa.Integer(), nullable=False, server_default="1"),
        sa.UniqueConstraint("upload_id", "fingerprint", name="uq_scan_findings_upload_fingerprint"),
    )
    for column in ("upload_id", "project_id", "scan_run_id", "bug_id"):
        op.create_index(f"ix_scan_findings_{column}", "scan_findings", [column])
    op.create_index("ix_scan_findings_project_severity", "scan_findings", ["project_id", "severity"])

    op.create_table(
        "scan_jobs",
        sa.Column("id", sa.String(length=32), primary_key=True),
        sa.Column("upload_id", sa.String(length=32), sa.ForeignKey("project_uploads.upload_id"), nullable=False),
        sa.Column("owner_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False, server_default="QUEUED"),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("result", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("error_message", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_scan_jobs_upload_id", "scan_jobs", ["upload_id"])
    op.create_index("ix_scan_jobs_owner_id", "scan_jobs", ["owner_id"])
    op.create_index("ix_scan_jobs_status", "scan_jobs", ["status"])
    op.create_index("ix_scan_jobs_status_created", "scan_jobs", ["status", "created_at"])


def downgrade() -> None:
    op.drop_table("scan_jobs")
    op.drop_table("scan_findings")
    op.drop_table("scan_runs")
