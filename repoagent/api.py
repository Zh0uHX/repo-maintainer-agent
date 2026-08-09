from __future__ import annotations

import json
import os
from pathlib import Path

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import HTMLResponse
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover - depends on optional package
    raise RuntimeError("Install API dependencies with: pip install -e '.[api]'") from exc

from . import __version__
from .agent import RepositoryAgent
from .config import AgentConfig
from .dashboard import DASHBOARD_HTML
from .runstore import history_report, load_run


class RunRequest(BaseModel):
    task: str = Field(min_length=1, max_length=10_000)
    root: str = "."
    apply_changes: bool = False
    max_steps: int = Field(default=18, ge=1, le=50)
    enable_ast_tools: bool = True
    enable_context_retrieval: bool = True


app = FastAPI(title="Repo Maintainer Agent", version=__version__)


def _allowed_root() -> Path:
    return Path(os.getenv("REPO_AGENT_ALLOWED_ROOT", ".")).resolve()


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    return DASHBOARD_HTML


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/history")
def get_history() -> dict:
    return history_report(_allowed_root())


@app.get("/runs/{run_id}")
def get_run(run_id: str) -> dict:
    try:
        return load_run(_allowed_root(), run_id)
    except (ValueError, FileNotFoundError, OSError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/runs")
def create_run(request: RunRequest) -> dict:
    allowed_root = _allowed_root()
    requested_root = Path(request.root).resolve()
    try:
        requested_root.relative_to(allowed_root)
    except ValueError:
        raise HTTPException(
            status_code=403, detail="root is outside REPO_AGENT_ALLOWED_ROOT"
        ) from None
    if request.apply_changes and os.getenv("REPO_AGENT_ALLOW_WRITES") != "1":
        raise HTTPException(status_code=403, detail="server-side writes are disabled")
    try:
        config = AgentConfig.from_env(
            requested_root,
            apply_changes=request.apply_changes,
            allow_checks=os.getenv("REPO_AGENT_ALLOW_CHECKS") == "1",
            enable_ast_tools=request.enable_ast_tools,
            enable_context_retrieval=request.enable_context_retrieval,
            max_steps=request.max_steps,
        )
        return RepositoryAgent(config).run(request.task).to_dict()
    except (ValueError, RuntimeError, OSError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
