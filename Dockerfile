FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    REPO_AGENT_ALLOWED_ROOT=/workspace

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY repoagent ./repoagent
RUN python -m pip install --no-cache-dir '.[api]'

EXPOSE 8000
CMD ["uvicorn", "repoagent.api:app", "--host", "0.0.0.0", "--port", "8000"]
