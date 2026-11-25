import uuid
import zipfile
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.database import Base
from app.models import Bug, ProjectUpload, ScanJob, ScanRun, User
from app import worker


def test_worker_processes_queued_scan_and_persists_findings(tmp_path, monkeypatch):
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    monkeypatch.setattr(worker, "SessionLocal", factory)
    monkeypatch.setattr(worker, "PROJECT_UPLOAD_DIR", tmp_path)
    upload_id = uuid.uuid4().hex
    with factory() as db:
        user = User(name="Worker test", email=f"{upload_id}@example.com", password_hash="hash", role="DEVELOPER")
        db.add(user); db.flush()
        db.add(ProjectUpload(upload_id=upload_id, owner_id=user.id))
        db.add(ScanJob(id=uuid.uuid4().hex, upload_id=upload_id, owner_id=user.id, status="QUEUED", result={}))
        db.commit()
        job_id = db.query(ScanJob).one().id
    with zipfile.ZipFile(tmp_path / f"{upload_id}.zip", "w") as archive:
        archive.writestr("src/broken.py", "def broken(:\n    pass\n")

    assert worker.process_one() is True
    with factory() as db:
        job = db.get(ScanJob, job_id)
        assert job.status == "COMPLETED"
        assert job.progress == 100
        assert job.result["scan_run_id"]
        assert db.query(ScanRun).count() == 1
        assert db.query(Bug).count() == 1
    engine.dispose()
