from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any


def summarize_trace(
    trace_path: Path,
    *,
    status: str,
    changed_files: int,
    checks: list[dict[str, Any]],
) -> dict[str, Any]:
    tool_counts: Counter[str] = Counter()
    model_calls = 0
    model_errors = 0
    request_attempts = 0
    parse_retries = 0
    model_latency_ms = 0
    tool_errors = 0
    total_tokens = 0
    input_tokens = 0
    output_tokens = 0
    provider_models: set[str] = set()
    steps: set[int] = set()

    for line in trace_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        payload = record.get("payload", {})
        if record.get("event") in {"model_response", "model_error"}:
            model_calls += 1
            if record.get("event") == "model_error":
                model_errors += 1
            model_latency_ms += int(payload.get("latency_ms", 0))
            metadata = payload.get("model_metadata", {})
            usage = metadata.get("usage", {})
            provider_model = metadata.get("model")
            request_attempts += _nonnegative_integer(metadata.get("request_attempts"), 1)
            parse_retries += _nonnegative_integer(metadata.get("parse_retries"), 0)
            if isinstance(provider_model, str) and provider_model:
                provider_models.add(provider_model)
            input_tokens += _integer_usage(usage, "prompt_tokens", "input_tokens")
            output_tokens += _integer_usage(usage, "completion_tokens", "output_tokens")
            total_tokens += _integer_usage(usage, "total_tokens")
        elif record.get("event") == "tool_observation":
            step = payload.get("step")
            if isinstance(step, int):
                steps.add(step)
            tool = payload.get("tool")
            if isinstance(tool, str):
                tool_counts[tool] += 1
            if not payload.get("ok", False):
                tool_errors += 1
        elif record.get("event") == "finish":
            step = payload.get("step")
            if isinstance(step, int):
                steps.add(step)

    if not total_tokens:
        total_tokens = input_tokens + output_tokens
    checks_passed = sum(item.get("exit_code") == 0 and not item.get("timed_out") for item in checks)
    return {
        "completed": status == "completed",
        "steps": max(steps, default=0),
        "model_calls": model_calls,
        "model_errors": model_errors,
        "request_attempts": request_attempts,
        "parse_retries": parse_retries,
        "model_latency_ms": model_latency_ms,
        "tool_calls": sum(tool_counts.values()),
        "tool_errors": tool_errors,
        "tool_counts": dict(sorted(tool_counts.items())),
        "changed_files": changed_files,
        "checks_passed": checks_passed,
        "checks_failed": len(checks) - checks_passed,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "provider_models": sorted(provider_models),
    }


def aggregate_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(results)
    passed = sum(bool(item.get("passed")) for item in results)
    metrics = [item.get("metrics", {}) for item in results]
    tool_counts: Counter[str] = Counter()
    provider_models: set[str] = set()
    for item in metrics:
        tool_counts.update(item.get("tool_counts", {}))
        provider_models.update(item.get("provider_models", []))
    families: dict[str, dict[str, Any]] = {}
    for item in results:
        family = str(item.get("family", "uncategorized"))
        bucket = families.setdefault(family, {"total": 0, "passed": 0})
        bucket["total"] += 1
        bucket["passed"] += int(bool(item.get("passed")))
    for bucket in families.values():
        bucket["pass_rate"] = round(bucket["passed"] / bucket["total"], 4)
    return {
        "total": total,
        "passed": passed,
        "pass_rate": round(passed / total, 4) if total else 0.0,
        "average_steps": _average(metrics, "steps"),
        "average_tool_calls": _average(metrics, "tool_calls"),
        "tool_errors": sum(int(item.get("tool_errors", 0)) for item in metrics),
        "model_errors": sum(int(item.get("model_errors", 0)) for item in metrics),
        "request_attempts": sum(int(item.get("request_attempts", 0)) for item in metrics),
        "parse_retries": sum(int(item.get("parse_retries", 0)) for item in metrics),
        "total_tokens": sum(int(item.get("total_tokens", 0)) for item in metrics),
        "tool_counts": dict(sorted(tool_counts.items())),
        "ast_tool_calls": tool_counts["inspect_python"] + tool_counts["symbol_search"],
        "context_retrieval_calls": tool_counts["retrieve_context"],
        "provider_models": sorted(provider_models),
        "families": dict(sorted(families.items())),
    }


def _integer_usage(usage: Any, *names: str) -> int:
    if not isinstance(usage, dict):
        return 0
    for name in names:
        value = usage.get(name)
        if isinstance(value, int):
            return value
    return 0


def _nonnegative_integer(value: Any, default: int) -> int:
    return value if isinstance(value, int) and value >= 0 else default


def _average(items: list[dict[str, Any]], key: str) -> float:
    if not items:
        return 0.0
    return round(sum(float(item.get(key, 0)) for item in items) / len(items), 2)
