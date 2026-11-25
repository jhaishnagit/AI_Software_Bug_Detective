from pathlib import Path

from app.test_runner.source_checker import check_project_source


def test_python_syntax_and_security_findings_are_reported(tmp_path):
    (tmp_path / "good.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    (tmp_path / "unsafe.py").write_text(
        "API_KEY = 'this-is-a-hardcoded-secret-value'\nuser_input = input()\neval(user_input)\n",
        encoding="utf-8",
    )
    result = check_project_source(tmp_path)
    checks = [item["check"] for item in result["results"]]
    assert any("PY syntax: good.py" in item for item in checks)
    assert any("HARDCODED_CREDENTIAL" in item for item in checks)
    assert any("DYNAMIC_EVAL" in item for item in checks)
    assert "Python" in result["languages_detected"]


def test_invalid_json_manifest_is_a_finding(tmp_path):
    (tmp_path / "package.json").write_text('{"name": }', encoding="utf-8")
    result = check_project_source(tmp_path)
    assert result["failed"] >= 1
    assert any("package.json" in item["check"] for item in result["results"])


def test_security_finding_includes_category_severity_and_line(tmp_path):
    (tmp_path / "danger.py").write_text("safe = 1\neval(user_input)\n", encoding="utf-8")
    result = check_project_source(tmp_path)
    finding = next(item for item in result["results"] if "DYNAMIC_EVAL" in item["check"])
    assert finding["category"] == "SECURITY"
    assert finding["severity"] == "HIGH"
    assert finding["line_number"] == 2
