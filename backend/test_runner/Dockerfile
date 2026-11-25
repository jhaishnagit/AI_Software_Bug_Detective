FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/tmp \
    PYTEST_ADDOPTS="-p no:cacheprovider"

RUN pip install --no-cache-dir "pytest>=8.0,<9.0"

WORKDIR /workspace
USER 65534:65534

ENTRYPOINT []
