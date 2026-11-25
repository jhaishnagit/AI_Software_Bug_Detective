"""Run the durable scan queue: python -m app.worker [--once]."""
from __future__ import annotations
import argparse
import tempfile
import time
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

from app.config.database import SessionLocal
from app.config.settings import settings
from app.models import ScanJob, User, ProjectUpload
from app.main import PROJECT_UPLOAD_DIR, MAX_PROJECT_FILES, persist_scan_results
from app.test_runner.source_checker import check_project_source

MAX_EXPANDED_BYTES = 200 * 1024 * 1024
MAX_FILE_BYTES = 1 * 1024 * 1024


def _claim_job():
    db = SessionLocal()
    try:
        job = db.query(ScanJob).filter(ScanJob.status == "QUEUED").order_by(ScanJob.created_at.asc()).first()
        if not job:
            return None
        changed = db.query(ScanJob).filter(ScanJob.id == job.id, ScanJob.status == "QUEUED").update({ScanJob.status: "RUNNING", ScanJob.started_at: datetime.now(timezone.utc), ScanJob.progress: 5}, synchronize_session=False)
        db.commit()
        return job.id if changed == 1 else None
    finally:
        db.close()


def process_one() -> bool:
    job_id = _claim_job()
    if not job_id:
        return False
    db = SessionLocal()
    started = time.perf_counter()
    try:
        job = db.get(ScanJob, job_id)
        if not job:
            return True
        user = db.get(User, job.owner_id)
        upload = db.get(ProjectUpload, job.upload_id)
        zip_path = PROJECT_UPLOAD_DIR / f"{job.upload_id}.zip"
        if not user or not upload or not zip_path.is_file():
            raise RuntimeError("The uploaded project archive or owner record was not found.")
        with zipfile.ZipFile(zip_path, "r") as archive, tempfile.TemporaryDirectory(prefix="bug-detective-worker-") as td:
            entries = [e for e in archive.infolist() if not e.is_dir()]
            if len(entries) > MAX_PROJECT_FILES:
                raise RuntimeError(f"Archive exceeds the {MAX_PROJECT_FILES} file limit.")
            total = sum(e.file_size for e in entries)
            if total > MAX_EXPANDED_BYTES:
                raise RuntimeError("Archive expands beyond the 200 MB safety limit.")
            root = Path(td).resolve()
            for entry in archive.infolist():
                raw = entry.filename.replace("\\", "/")
                member = PurePosixPath(raw)
                if member.is_absolute() or ".." in member.parts or (member.parts and ":" in member.parts[0]):
                    raise RuntimeError("Archive contains an unsafe path.")
                if entry.is_dir():
                    continue
                if entry.file_size > MAX_FILE_BYTES:
                    continue
                dest = (root / Path(*member.parts)).resolve()
                if not dest.is_relative_to(root):
                    raise RuntimeError("Archive contains a path traversal entry.")
                dest.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(entry) as src, dest.open("wb") as out:
                    out.write(src.read(MAX_FILE_BYTES + 1))
            result = check_project_source(root)
        counts = {key: result.get(key, 0) for key in ("total_checks", "passed", "failed", "errors", "skipped")}
        persistence = persist_scan_results(job.upload_id, user, db, result.get("results", []), counts, result.get("files_checked", 0), time.perf_counter() - started)
        job = db.get(ScanJob, job_id)
        job.status = "COMPLETED"
        job.progress = 100
        job.result = {**{k: result.get(k) for k in ("status", "execution_mode", "total_checks", "passed", "failed", "errors", "skipped", "files_checked", "languages_detected", "note")}, **persistence}
        job.completed_at = datetime.now(timezone.utc)
        db.commit()
    except Exception as exc:
        db.rollback()
        job = db.get(ScanJob, job_id)
        if job:
            job.status = "FAILED"
            job.error_message = f"{type(exc).__name__}: {str(exc)[:700]}"
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
    finally:
        db.close()
    return True


def main():
    parser = argparse.ArgumentParser(description="AI Software Bug Detective scan worker")
    parser.add_argument("--once", action="store_true", help="Process at most one queued scan and exit")
    parser.add_argument("--poll-seconds", type=float, default=2.0)
    args = parser.parse_args()
    while True:
        processed = process_one()
        if args.once:
            break
        if not processed:
            time.sleep(max(0.5, args.poll_seconds))


if __name__ == "__main__":
    main()
