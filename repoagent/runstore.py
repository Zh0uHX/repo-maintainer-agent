from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

RUN_ID_PATTERN = re.compile(r"[A-Za-z0-9_-]+")


def safe_runs_dir(root: Path, *, create: bool = False) -> Path:
    root = root.expanduser().resolve()
    internal = root / ".repoagent"
    runs = internal / "runs"
    for candidate in (internal, runs):
        if candidate.is_symlink():
            raise ValueError(f"Agent storage cannot be a symbolic link: {candidate}")
    if create:
        runs.mkdir(parents=True, exist_ok=True)
    if runs.exists():
        try:
            runs.resolve().relative_to(root)
        except ValueError:
            raise ValueError("Agent storage escapes repository root.") from None
    return runs


def list_runs(root: Path) -> list[dict[str, Any]]:
    runs_dir = safe_runs_dir(root)
    if not runs_dir.is_dir():
        return []
    runs: list[dict[str, Any]] = []
    for directory in runs_dir.iterdir():
        result_path = directory / "result.json"
        if directory.is_symlink() or result_path.is_symlink():
            continue
        if not directory.is_dir() or not result_path.is_file():
            continue
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        runs.append(
            {
                "run_id": directory.name,
                "status": result.get("status", "unknown"),
                "summary": result.get("summary", ""),
                "changed_files": result.get("changed_files", []),
                "metrics": result.get("metrics", {}),
            }
        )
    return sorted(runs, key=lambda item: item["run_id"], reverse=True)


def load_run(root: Path, run_id: str) -> dict[str, Any]:
    if not RUN_ID_PATTERN.fullmatch(run_id):
        raise ValueError("Invalid run id.")
    run_dir = safe_runs_dir(root) / run_id
    result_path = run_dir / "result.json"
    trace_path = run_dir / "trace.jsonl"
    if run_dir.is_symlink() or result_path.is_symlink() or trace_path.is_symlink():
        raise ValueError("Run storage contains a symbolic link.")
    if not result_path.is_file():
        raise FileNotFoundError(f"Run not found: {run_id}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    trace = []
    if trace_path.is_file():
        for line in trace_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                trace.append(json.loads(line))
    return {"result": result, "trace": trace}


def history_report(root: Path) -> dict[str, Any]:
    runs = list_runs(root)
    completed = sum(item["status"] == "completed" for item in runs)
    metrics = [item.get("metrics", {}) for item in runs]
    total = len(runs)
    return {
        "total_runs": total,
        "completed_runs": completed,
        "completion_rate": round(completed / total, 4) if total else 0.0,
        "changed_files": sum(int(item.get("changed_files", 0)) for item in metrics),
        "tool_calls": sum(int(item.get("tool_calls", 0)) for item in metrics),
        "tool_errors": sum(int(item.get("tool_errors", 0)) for item in metrics),
        "total_tokens": sum(int(item.get("total_tokens", 0)) for item in metrics),
        "runs": runs,
    }
