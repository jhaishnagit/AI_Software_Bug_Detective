"""Safe multi-language source, security and performance heuristics.

Uploaded code is parsed/read only; this module never imports or executes it.
"""
from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

MAX_FILE_BYTES = 1 * 1024 * 1024
IGNORE_DIRS = {"node_modules", ".git", ".venv", "venv", "__pycache__", "dist", "build", ".next", "target", "vendor"}
SOURCE_SUFFIXES = {".py", ".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".java", ".php", ".go", ".rb"}
TEXT_CONFIGS = {"package.json", "composer.json", "pom.xml", "go.mod", "requirements.txt", "pyproject.toml"}


def _result(check: str, status: str, details: str, *, category: str = "QUALITY", severity: str = "INFO", file: str = "", line: int | None = None) -> dict:
    return {"check": check[:240], "status": status, "details": details[:1000], "category": category, "severity": severity, "source_file": file[:512], "line_number": line}


def _parse_javascript(path: Path, source: str, frontend_dir: Path) -> tuple[str, str]:
    parser_dir = frontend_dir / "node_modules" / "@babel" / "parser"
    if not parser_dir.is_dir() or shutil.which("node") is None:
        return "SKIPPED", "Install frontend dependencies (npm install) to enable Babel syntax parsing."
    script = r'''const fs=require('fs'); const parser=require('@babel/parser'); const f=process.argv[1]; const s=fs.readFileSync(f,'utf8'); const e=f.split('.').pop().toLowerCase(); const p=[]; if(e==='jsx'||e==='tsx')p.push('jsx'); if(e==='ts'||e==='tsx')p.push('typescript'); parser.parse(s,{sourceType:'unambiguous',plugins:p}); process.stdout.write('Syntax is valid');'''
    try:
        done = subprocess.run(["node", "-e", script, str(path)], cwd=str(frontend_dir), capture_output=True, text=True, timeout=12, check=False, shell=False)
        return ("PASS", "JavaScript/TypeScript syntax parsed successfully.") if done.returncode == 0 else ("FAIL", (done.stderr or done.stdout or "Parser failed.")[-900:])
    except subprocess.TimeoutExpired:
        return "ERROR", "Syntax parsing exceeded the 12-second limit."


def _language_syntax(path: Path, source: str, frontend_dir: Path) -> tuple[str, str] | None:
    suffix = path.suffix.lower()
    if suffix == ".py":
        try:
            ast.parse(source, filename=str(path)); return "PASS", "Python syntax is valid; code was not executed."
        except SyntaxError as exc:
            return "FAIL", f"Syntax error at line {exc.lineno}: {exc.msg}"
    if suffix in {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx"}:
        return _parse_javascript(path, source, frontend_dir)
    if suffix == ".java" and shutil.which("javac"):
        with __import__('tempfile').TemporaryDirectory(prefix="bugdetect-java-") as td:
            temp = Path(td) / path.name; temp.write_text(source, encoding="utf-8")
            try:
                done = subprocess.run(["javac", "-proc:none", str(temp)], capture_output=True, text=True, timeout=15, check=False, shell=False)
                return ("PASS", "Java syntax compilation passed (annotation processing disabled).") if done.returncode == 0 else ("FAIL", (done.stderr or done.stdout or "javac failed")[-900:])
            except subprocess.TimeoutExpired: return "ERROR", "javac exceeded the 15-second limit."
    if suffix == ".php" and shutil.which("php"):
        done = subprocess.run(["php", "-l"], input=source, capture_output=True, text=True, timeout=10, check=False, shell=False)
        return ("PASS", "PHP syntax check passed.") if done.returncode == 0 else ("FAIL", (done.stderr or done.stdout or "PHP syntax error")[-900:])
    if suffix == ".rb" and shutil.which("ruby"):
        done = subprocess.run(["ruby", "-c"], input=source, capture_output=True, text=True, timeout=10, check=False, shell=False)
        return ("PASS", "Ruby syntax check passed.") if done.returncode == 0 else ("FAIL", (done.stderr or done.stdout or "Ruby syntax error")[-900:])
    if suffix == ".go" and shutil.which("gofmt"):
        done = subprocess.run(["gofmt", "-e"], input=source, capture_output=True, text=True, timeout=10, check=False, shell=False)
        return ("PASS", "Go source parsed by gofmt.") if done.returncode == 0 else ("FAIL", (done.stderr or done.stdout or "Go parse error")[-900:])
    return None


SECRET_PATTERNS = [
    ("HARDCODED_CREDENTIAL", re.compile(r"(?i)(api[_-]?key|secret|password|access[_-]?token)\s*[:=]\s*['\"][^'\"]{8,}['\"]"), "Possible hard-coded credential. Move it to a secret manager or environment variable."),
    ("PRIVATE_KEY", re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"), "Private key material appears in source. Remove it and rotate the exposed key."),
]
SECURITY_PATTERNS = [
    ("DYNAMIC_EVAL", re.compile(r"\beval\s*\("), "Dynamic eval can execute untrusted input. Validate input and avoid eval."),
    ("SHELL_EXECUTION", re.compile(r"(?i)(shell\s*=\s*True|os\.system\s*\(|child_process\.exec\s*\()"), "Shell command execution detected. Use argument arrays and validate inputs."),
    ("INSECURE_TLS", re.compile(r"(?i)(verify\s*=\s*False|rejectUnauthorized\s*:\s*false)"), "TLS certificate verification appears disabled."),
]
PERFORMANCE_PATTERNS = [
    ("POSSIBLE_N_PLUS_ONE", re.compile(r"(?i)for\s+\w+\s+in\s+[^:]+:\s*\n(?:\s+.*\n){0,4}\s+.*\.(?:query|execute)\s*\("), "Possible database query inside a loop; consider batching or eager loading."),
    ("UNBOUNDED_READ", re.compile(r"(?i)read_text\s*\(\s*\)|read\s*\(\s*\)"), "Unbounded file read detected. Consider streaming or enforcing size limits."),
]


def check_project_source(project_dir: str | Path) -> dict:
    root = Path(project_dir).resolve()
    if not root.is_dir():
        return {"status": "ERROR", "message": "Project directory was not found.", "total_checks": 0, "passed": 0, "failed": 0, "errors": 1, "skipped": 0, "files_checked": 0, "results": []}
    app_root = Path(__file__).resolve().parents[3]
    frontend_dir = app_root / "frontend"
    results: list[dict] = []
    files_checked = 0
    supported_languages: set[str] = set()
    for current, dirs, names in __import__('os').walk(root):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for name in names:
            path = Path(current) / name
            rel = path.relative_to(root).as_posix()
            suffix = path.suffix.lower()
            if suffix not in SOURCE_SUFFIXES and name.lower() not in TEXT_CONFIGS and suffix not in {".json", ".xml", ".yaml", ".yml"}:
                continue
            try:
                size = path.stat().st_size
                if size > MAX_FILE_BYTES:
                    results.append(_result(f"Source check: {rel}", "SKIPPED", "File exceeds the 1 MB safe analysis limit.", file=rel)); continue
                source = path.read_text(encoding="utf-8")
                files_checked += 1
                if suffix in SOURCE_SUFFIXES:
                    supported_languages.add({".py":"Python", ".js":"JavaScript", ".jsx":"React JSX", ".mjs":"JavaScript", ".cjs":"JavaScript", ".ts":"TypeScript", ".tsx":"React TypeScript", ".java":"Java", ".php":"PHP", ".go":"Go", ".rb":"Ruby"}[suffix])
                    syntax = _language_syntax(path, source, frontend_dir)
                    if syntax:
                        results.append(_result(f"{path.suffix[1:].upper()} syntax: {rel}", syntax[0], syntax[1], category="SYNTAX", severity="HIGH" if syntax[0] == "FAIL" else "INFO", file=rel))
                    else:
                        results.append(_result(f"{path.suffix[1:].upper()} syntax: {rel}", "SKIPPED", f"No safe parser/compiler found for {path.suffix}; install the language toolchain to enable this check.", category="SYNTAX", file=rel))
                elif name.lower() in {"package.json", "composer.json"} or suffix == ".json":
                    json.loads(source)
                    results.append(_result(f"JSON manifest: {rel}", "PASS", "Valid JSON.", category="CONFIG", file=rel))
                elif suffix == ".xml" or name.lower() == "pom.xml":
                    ET.fromstring(source)
                    results.append(_result(f"XML manifest: {rel}", "PASS", "Valid XML.", category="CONFIG", file=rel))
                elif suffix in {".yaml", ".yml"}:
                    try:
                        import yaml
                        yaml.safe_load(source)
                        results.append(_result(f"YAML config: {rel}", "PASS", "Valid YAML.", category="CONFIG", file=rel))
                    except ImportError:
                        results.append(_result(f"YAML config: {rel}", "SKIPPED", "Install PyYAML to enable YAML parsing.", category="CONFIG", file=rel))
                # Lightweight security/performance heuristics. Findings are review signals, not proof of exploitability.
                for code, pattern, message in SECRET_PATTERNS:
                    match = pattern.search(source)
                    if match:
                        line = source.count("\n", 0, match.start()) + 1
                        results.append(_result(f"Security {code}: {rel}", "FAIL", message, category="SECURITY", severity="CRITICAL", file=rel, line=line))
                for code, pattern, message in SECURITY_PATTERNS:
                    match = pattern.search(source)
                    if match:
                        line = source.count("\n", 0, match.start()) + 1
                        results.append(_result(f"Security {code}: {rel}", "FAIL", message, category="SECURITY", severity="HIGH", file=rel, line=line))
                for code, pattern, message in PERFORMANCE_PATTERNS:
                    match = pattern.search(source)
                    if match:
                        line = source.count("\n", 0, match.start()) + 1
                        results.append(_result(f"Performance {code}: {rel}", "FAIL", message, category="PERFORMANCE", severity="MEDIUM", file=rel, line=line))
            except (UnicodeDecodeError, json.JSONDecodeError, ET.ParseError, ValueError) as exc:
                results.append(_result(f"Source/config validation: {rel}", "FAIL", f"Invalid text/config: {type(exc).__name__}: {str(exc)[:300]}", category="CONFIG", severity="MEDIUM", file=rel))
            except (OSError, subprocess.SubprocessError) as exc:
                results.append(_result(f"Source check: {rel}", "ERROR", f"Unable to analyze file: {type(exc).__name__}.", file=rel))
    passed = sum(x["status"] == "PASS" for x in results)
    failed = sum(x["status"] == "FAIL" for x in results)
    errors = sum(x["status"] == "ERROR" for x in results)
    skipped = sum(x["status"] == "SKIPPED" for x in results)
    return {"status": "CHECKS_COMPLETED", "execution_mode": "STATIC_SAFE_CHECKS", "total_checks": len(results), "passed": passed, "failed": failed, "errors": errors, "skipped": skipped, "files_checked": files_checked, "languages_detected": sorted(supported_languages), "results": results, "note": "Static syntax, configuration, and heuristic security/performance checks only. Findings require human review; uploaded code was not executed and this is not a replacement for SAST/DAST or runtime tests."}
