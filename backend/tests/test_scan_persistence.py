import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.config.database import Base
from app.models import Bug, ProjectUpload, ScanFinding, ScanRun, User


def test_static_scan_persists_bug_and_deduplicates_repeat_finding():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = session_factory()
    try:
        user = User(
            name="Scan Test",
            email=f"scan-{uuid.uuid4().hex}@example.com",
            password_hash="not-a-real-password-hash",
            role="DEVELOPER",
        )
        db.add(user)
        db.flush()
        upload_id = uuid.uuid4().hex
        db.add(ProjectUpload(upload_id=upload_id, owner_id=user.id))
        db.commit()

        results = [{
            "check": "Source syntax: src/broken.py",
            "status": "FAIL",
            "details": "Syntax error at line 12.",
        }]
        counts = {"total_checks": 1, "passed": 0, "failed": 1, "errors": 0, "skipped": 0}

        first = main.persist_scan_results(upload_id, user, db, results, counts, 1, 0.12)
        assert first["scan_status"] == "ISSUES_FOUND"
        assert len(first["detected_bugs"]) == 1
        assert db.query(Bug).count() == 1
        assert db.query(ScanRun).count() == 1
        assert db.query(ScanFinding).count() == 1

        second = main.persist_scan_results(upload_id, user, db, results, counts, 1, 0.09)
        assert len(second["detected_bugs"]) == 1
        assert db.query(Bug).count() == 1
        assert db.query(ScanRun).count() == 2
        finding = db.query(ScanFinding).one()
        assert finding.occurrence_count == 2
        assert finding.bug_id == first["detected_bugs"][0]["bug_id"]
    finally:
        db.close()
        engine.dispose()


def test_scan_api_creates_bug_tracker_record_and_pdf_report(tmp_path, monkeypatch):
    import io
    import zipfile
    from fastapi.testclient import TestClient
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    from app.config.database import get_db

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setattr(main, "PROJECT_UPLOAD_DIR", tmp_path)
    main.app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(main.app) as client:
            registered = client.post("/api/auth/register", json={
                "name": "Scan API Test",
                "email": f"scan-api-{uuid.uuid4().hex}@example.com",
                "password": "test-password-123",
            })
            assert registered.status_code == 201, registered.text
            headers = {"Authorization": f"Bearer {registered.json()['access_token']}"}

            archive_data = io.BytesIO()
            with zipfile.ZipFile(archive_data, "w") as archive:
                archive.writestr("sample/broken.py", "def broken(:\n    pass\n")

            uploaded = client.post(
                "/api/projects/upload-source", headers=headers,
                files={"file": ("sample-project.zip", archive_data.getvalue(), "application/zip")},
            )
            assert uploaded.status_code == 200, uploaded.text
            upload_id = uploaded.json()["upload_id"]

            scan = client.post(f"/api/projects/{upload_id}/run-tests", headers=headers)
            assert scan.status_code == 200, scan.text
            scan_data = scan.json()
            assert scan_data["scan_run_id"]
            assert len(scan_data["detected_bugs"]) == 1

            bugs = client.get("/api/bugs", headers=headers)
            assert bugs.status_code == 200
            assert len(bugs.json()) == 1

            history = client.get("/api/scan-runs", headers=headers)
            assert history.status_code == 200
            assert len(history.json()) == 1

            queued = client.post(f"/api/projects/{upload_id}/scan-jobs", headers=headers)
            assert queued.status_code == 202, queued.text
            job_id = queued.json()["job_id"]
            job_status = client.get(f"/api/scan-jobs/{job_id}", headers=headers)
            assert job_status.status_code == 200, job_status.text
            assert job_status.json()["status"] == "QUEUED"

            execution = client.post(f"/api/projects/{upload_id}/execute-tests", headers=headers)
            assert execution.status_code == 200, execution.text
            execution_history = client.get(
                f"/api/projects/{upload_id}/execution-history", headers=headers
            )
            assert execution_history.status_code == 200
            assert len(execution_history.json()) == 1

            pdf = client.get(f"/api/projects/{upload_id}/test-report/pdf", headers=headers)
            assert pdf.status_code == 200, pdf.text
            assert pdf.headers["content-type"].startswith("application/pdf")
            assert pdf.content.startswith(b"%PDF")
    finally:
        main.app.dependency_overrides.pop(get_db, None)
        engine.dispose()
