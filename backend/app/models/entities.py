from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Index, Integer, JSON, String, Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.config.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(30), default="DEVELOPER")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    projects: Mapped[list["Project"]] = relationship(back_populates="owner")


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(180), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    technology: Mapped[str] = mapped_column(String(255), default="")
    repository_url: Mapped[str] = mapped_column(String(500), default="")
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    owner: Mapped[User] = relationship(back_populates="projects")
    bugs: Mapped[list["Bug"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    uploads: Mapped[list["ProjectUpload"]] = relationship(back_populates="project")


class ProjectUpload(Base):
    __tablename__ = "project_uploads"

    upload_id: Mapped[str] = mapped_column(String(32), primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    # This nullable FK already exists in the supplied PostgreSQL backup.
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)

    project: Mapped[Project | None] = relationship(back_populates="uploads")


class SourceChunk(Base):
    __tablename__ = "source_chunks"
    __table_args__ = (
        UniqueConstraint("upload_id", "source_name", "chunk_index"),
        Index("ix_source_chunks_owner_upload", "owner_id", "upload_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[str] = mapped_column(ForeignKey("project_uploads.upload_id"), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    source_name: Mapped[str] = mapped_column(String(512))
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Bug(Base):
    __tablename__ = "bugs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(220), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    error_message: Mapped[str] = mapped_column(Text, default="")
    reproduction_steps: Mapped[str] = mapped_column(Text, default="")
    expected_result: Mapped[str] = mapped_column(Text, default="")
    actual_result: Mapped[str] = mapped_column(Text, default="")
    module: Mapped[str] = mapped_column(String(120), default="General")
    environment: Mapped[str] = mapped_column(String(120), default="Development")
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    status: Mapped[str] = mapped_column(String(30), default="OPEN")
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    project: Mapped[Project] = relationship(back_populates="bugs")
    analyses: Mapped[list["BugAnalysis"]] = relationship(back_populates="bug", cascade="all, delete-orphan")
    attachments: Mapped[list["Attachment"]] = relationship(back_populates="bug", cascade="all, delete-orphan")
    test_cases: Mapped[list["TestCase"]] = relationship(back_populates="bug")
    scan_findings: Mapped[list["ScanFinding"]] = relationship(back_populates="bug")


class BugAnalysis(Base):
    __tablename__ = "bug_analysis"

    id: Mapped[int] = mapped_column(primary_key=True)
    bug_id: Mapped[int] = mapped_column(ForeignKey("bugs.id"), index=True)
    root_cause: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.4)
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    affected_component: Mapped[str] = mapped_column(String(180), default="Unknown")
    possible_causes: Mapped[str] = mapped_column(Text, default="")
    suggested_fix: Mapped[str] = mapped_column(Text, default="")
    recommended_actions: Mapped[str] = mapped_column(Text, default="")
    provider: Mapped[str] = mapped_column(String(40), default="mock")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    bug: Mapped[Bug] = relationship(back_populates="analyses")


class TestCase(Base):
    __tablename__ = "test_cases"
    __table_args__ = (
        UniqueConstraint("upload_id", "source_key", name="uq_test_cases_upload_source_key"),
        Index("ix_test_cases_project_upload", "project_id", "upload_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # Existing PostgreSQL schema permits project-level cases without a bug_id.
    bug_id: Mapped[int | None] = mapped_column(ForeignKey("bugs.id"), index=True, nullable=True)
    scenario: Mapped[str] = mapped_column(String(240))
    input_data: Mapped[str] = mapped_column(Text, default="")
    expected_result: Mapped[str] = mapped_column(Text, default="")
    priority: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    test_type: Mapped[str] = mapped_column(String(30), default="FUNCTIONAL")
    executed: Mapped[bool] = mapped_column(Boolean, default=False)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)
    upload_id: Mapped[str | None] = mapped_column(ForeignKey("project_uploads.upload_id"), nullable=True, index=True)
    source_key: Mapped[str | None] = mapped_column(String(64), nullable=True)

    bug: Mapped[Bug | None] = relationship(back_populates="test_cases")


class Attachment(Base):
    __tablename__ = "bug_attachments"

    id: Mapped[int] = mapped_column(primary_key=True)
    bug_id: Mapped[int] = mapped_column(ForeignKey("bugs.id"), index=True)
    original_name: Mapped[str] = mapped_column(String(255))
    stored_name: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    extracted_text: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    bug: Mapped[Bug] = relationship(back_populates="attachments")


class TestExecutionHistory(Base):
    __tablename__ = "test_execution_history"
    __table_args__ = (
        Index("ix_test_execution_history_project_created", "project_id", "started_at"),
        Index("ix_test_execution_history_upload_created", "upload_id", "started_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[str] = mapped_column(String(32), index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True, index=True)
    test_case_id: Mapped[int | None] = mapped_column(ForeignKey("test_cases.id"), nullable=True)
    initiated_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(40))
    execution_mode: Mapped[str] = mapped_column(String(40))
    total: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    runtime_executed: Mapped[bool] = mapped_column(Boolean, default=False)
    output: Mapped[str] = mapped_column(Text, default="")
    error_message: Mapped[str] = mapped_column(Text, default="")
    failure_reason: Mapped[str] = mapped_column(Text, default="")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class ScanRun(Base):
    __tablename__ = "scan_runs"
    __table_args__ = (Index("ix_scan_runs_project_created", "project_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[str] = mapped_column(ForeignKey("project_uploads.upload_id"), index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    initiated_by: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(40))
    execution_mode: Mapped[str] = mapped_column(String(40), default="STATIC_SAFE_CHECKS")
    total_checks: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    errors: Mapped[int] = mapped_column(Integer, default=0)
    skipped: Mapped[int] = mapped_column(Integer, default=0)
    files_checked: Mapped[int] = mapped_column(Integer, default=0)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0)
    summary: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    project: Mapped[Project] = relationship()


class ScanFinding(Base):
    __tablename__ = "scan_findings"
    __table_args__ = (
        UniqueConstraint("upload_id", "fingerprint", name="uq_scan_findings_upload_fingerprint"),
        Index("ix_scan_findings_project_severity", "project_id", "severity"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    upload_id: Mapped[str] = mapped_column(ForeignKey("project_uploads.upload_id"), index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    scan_run_id: Mapped[int] = mapped_column(ForeignKey("scan_runs.id"), index=True)
    bug_id: Mapped[int] = mapped_column(ForeignKey("bugs.id"), index=True)
    fingerprint: Mapped[str] = mapped_column(String(64))
    rule_code: Mapped[str] = mapped_column(String(80), default="STATIC_CHECK")
    source_file: Mapped[str] = mapped_column(String(512), default="")
    line_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    severity: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    finding_status: Mapped[str] = mapped_column(String(30), default="OPEN")
    title: Mapped[str] = mapped_column(String(220))
    details: Mapped[str] = mapped_column(Text, default="")
    root_cause: Mapped[str] = mapped_column(Text, default="")
    suggested_fix: Mapped[str] = mapped_column(Text, default="")
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    occurrence_count: Mapped[int] = mapped_column(Integer, default=1)

    bug: Mapped[Bug] = relationship(back_populates="scan_findings")


class ScanJob(Base):
    """Durable database-backed scan queue job."""
    __tablename__ = "scan_jobs"
    __table_args__ = (Index("ix_scan_jobs_status_created", "status", "created_at"),)

    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    upload_id: Mapped[str] = mapped_column(ForeignKey("project_uploads.upload_id"), index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    status: Mapped[str] = mapped_column(String(24), default="QUEUED", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    result: Mapped[dict] = mapped_column(JSON, default=dict)
    error_message: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
