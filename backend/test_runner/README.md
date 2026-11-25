# Isolated Python test runner image

Build the runner image once from the repository root:

```powershell
docker build -t ai-bug-detective-python-runner:latest -f backend/test_runner/Dockerfile backend/test_runner
```

The current runtime runner executes Python `pytest` from the uploaded project's `tests/` directory. The container is launched with no network, read-only source mount, memory/CPU/PID limits, dropped Linux capabilities, and a non-root user.

This image intentionally does not install dependencies from an untrusted uploaded `requirements.txt`. Projects that need additional test dependencies require a separately reviewed and trusted runner image. Java, Node.js, .NET, Go, and other language-specific runtime runners are not included yet; use static checks for those until dedicated sandbox images are implemented.
