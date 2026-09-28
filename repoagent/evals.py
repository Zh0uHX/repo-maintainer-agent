from __future__ import annotations

import json
import re
import shutil
import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Any

from .agent import RepositoryAgent
from .config import AgentConfig
from .llm import ModelClient, ProviderFatalError
from .metrics import aggregate_results, summarize_trace
from .realrepo import materialize, score_localization
from .tools import RepositoryTools, ToolError


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict) or "task" not in value:
                raise ValueError(f"Invalid benchmark case at line {number}.")
            cases.append(value)
    return cases


def merge_benchmark_reports(base: dict[str, Any], update: dict[str, Any]) -> dict[str, Any]:
    if base.get("model") != update.get("model"):
        raise ValueError("Cannot merge reports with different configured models.")
    if base.get("ast_enabled") != update.get("ast_enabled"):
        raise ValueError("Cannot merge reports with different AST configurations.")
    if base.get("context_retrieval_enabled", False) != update.get(
        "context_retrieval_enabled", False
    ):
        raise ValueError("Cannot merge reports with different context-retrieval configurations.")
    if bool(base.get("ast_guidance")) != bool(update.get("ast_guidance")):
        raise ValueError("Cannot merge reports with different AST guidance prompts.")
    replacements = {item["name"]: item for item in update.get("results", [])}
    merged_results = [replacements.pop(item["name"], item) for item in base.get("results", [])]
    merged_results.extend(replacements.values())
    return {
        "model": base.get("model"),
        "ast_enabled": base.get("ast_enabled"),
        "context_retrieval_enabled": base.get("context_retrieval_enabled", False),
        "ast_guidance": bool(base.get("ast_guidance")),
        **aggregate_results(merged_results),
        "results": merged_results,
    }


def evaluate_case(
    case: dict[str, Any],
    config: AgentConfig,
    client: ModelClient,
    artifacts_dir: Path | None = None,
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="repoagent-eval-") as temporary:
        root = Path(temporary)
        try:
            return _evaluate_case_in_root(case, config, client, artifacts_dir, root)
        except (OSError, RuntimeError, TypeError, ValueError, ToolError) as exc:
            result = _error_result(case, root, exc)
            result["fatal"] = isinstance(exc, ProviderFatalError)
            if artifacts_dir is not None:
                source = root / ".repoagent" if "repo" in case else root
                destination = _preserve_artifact(source, artifacts_dir, case)
                (destination / "evaluation-error.json").write_text(
                    json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8",
                )
            return result


def _evaluate_case_in_root(
    case: dict[str, Any],
    config: AgentConfig,
    client: ModelClient,
    artifacts_dir: Path | None,
    root: Path,
) -> dict[str, Any]:
    real_repo = "repo" in case
    mode = str(case.get("mode", "edit"))
    if real_repo:
        materialize(str(case["repo"]), str(case["base_commit"]), root)
    else:
        _write_fixture_files(root, case.get("files", {}))
    case_config = replace(
        config,
        root=root,
        task_mode=mode,
        apply_changes=mode == "edit",
        # Real repositories have no installed environment, so their checks cannot run locally.
        allow_checks=bool(case.get("allow_checks", not real_repo)),
    )
    result = RepositoryAgent(case_config, client).run(str(case["task"]))
    assertions: list[dict[str, Any]] = []
    localization = None
    if mode == "localize":
        localization = score_localization(result.locations, case.get("gold", {}))
        assertions.append({"type": "top1_location", "passed": localization_passed(localization)})
    for relative, expected in case.get("contains", {}).items():
        target = root / relative
        actual = target.read_text(encoding="utf-8") if target.exists() else ""
        passed = all(fragment in actual for fragment in expected)
        assertions.append({"type": "contains", "path": relative, "passed": passed})
    for relative, forbidden in case.get("not_contains", {}).items():
        target = root / relative
        actual = target.read_text(encoding="utf-8") if target.exists() else ""
        passed = all(fragment not in actual for fragment in forbidden)
        assertions.append({"type": "not_contains", "path": relative, "passed": passed})
    allowed_changes = case.get("allowed_changed_files")
    if isinstance(allowed_changes, list):
        unexpected = sorted(set(result.changed_files) - set(allowed_changes))
        assertions.append(
            {
                "type": "allowed_changed_files",
                "passed": not unexpected,
                "unexpected": unexpected,
            }
        )
    _write_fixture_files(root, case.get("hidden_files", {}))
    verifier = RepositoryTools(case_config, root / ".repoagent" / "benchmark-verification")
    benchmark_checks = []
    for command in case.get("check_commands", []):
        check = verifier.run_check(str(command))
        benchmark_checks.append(check)
        assertions.append(
            {
                "type": "check_command",
                "command": command,
                "passed": check["exit_code"] == 0 and not check["timed_out"],
            }
        )
    mutation_checks = []
    for mutation in case.get("mutations", []):
        if not isinstance(mutation, dict):
            raise TypeError("Each mutation must be an object.")
        relative = mutation.get("path")
        content = mutation.get("content")
        command = mutation.get("check_command", "python -m pytest -q")
        if not isinstance(relative, str) or not isinstance(content, str):
            raise TypeError("Mutation path and content must be strings.")
        target = _fixture_path(root, relative)
        if not target.is_file():
            raise ValueError(f"Mutation target does not exist: {relative}")
        original = target.read_text(encoding="utf-8")
        try:
            target.write_text(content, encoding="utf-8")
            check = verifier.run_check(str(command))
        finally:
            target.write_text(original, encoding="utf-8")
        killed = check["exit_code"] == 1 and not check["timed_out"]
        mutation_checks.append({"path": relative, "check": check, "killed": killed})
        assertions.append({"type": "mutation_killed", "path": relative, "passed": killed})
    passed = result.status == "completed" and all(item["passed"] for item in assertions)
    if artifacts_dir is not None:
        # A real repository can be hundreds of megabytes; keep only the Agent's run records.
        _preserve_artifact(root / ".repoagent" if real_repo else root, artifacts_dir, case)
    extra: dict[str, Any] = {}
    if localization is not None:
        extra["localization"] = localization
        extra["locations"] = result.locations
    if real_repo and mode == "edit":
        extra["model_patch"] = result.diff
    return {
        "name": case.get("name", case["task"]),
        "family": case.get("family", "uncategorized"),
        **({"instance_id": case["instance_id"]} if "instance_id" in case else {}),
        **extra,
        "passed": passed,
        "status": result.status,
        "summary": result.summary,
        "assertions": assertions,
        "changed_files": result.changed_files,
        "agent_checks": result.checks,
        "benchmark_checks": benchmark_checks,
        "mutation_checks": mutation_checks,
        "metrics": result.metrics,
    }


def _error_result(case: dict[str, Any], root: Path, exc: Exception) -> dict[str, Any]:
    trace_paths = sorted((root / ".repoagent" / "runs").glob("*/trace.jsonl"))
    metrics = (
        summarize_trace(
            trace_paths[-1],
            status="error",
            changed_files=0,
            checks=[],
        )
        if trace_paths
        else _empty_metrics()
    )
    return {
        "name": case.get("name", case.get("task", "unnamed")),
        "family": case.get("family", "uncategorized"),
        "passed": False,
        "status": "error",
        "error": f"{type(exc).__name__}: {exc}",
        "assertions": [],
        "changed_files": [],
        "agent_checks": [],
        "benchmark_checks": [],
        "mutation_checks": [],
        "metrics": metrics,
    }


def _empty_metrics() -> dict[str, Any]:
    return {
        "completed": False,
        "steps": 0,
        "model_calls": 0,
        "model_errors": 0,
        "request_attempts": 0,
        "parse_retries": 0,
        "closed_brackets": 0,
        "model_latency_ms": 0,
        "tool_calls": 0,
        "tool_errors": 0,
        "tool_counts": {},
        "context_retrieval_calls": 0,
        "changed_files": 0,
        "checks_passed": 0,
        "checks_failed": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "total_tokens": 0,
        "provider_models": [],
    }


def _preserve_artifact(root: Path, artifacts_dir: Path, case: dict[str, Any]) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "-", str(case.get("name", "case"))).strip("-")
    destination = artifacts_dir / (safe_name or "case")
    destination.mkdir(parents=True, exist_ok=True)
    if root.exists():
        shutil.copytree(root, destination, dirs_exist_ok=True)
    return destination


def copy_fixture(source: Path, destination: Path) -> None:
    """Public helper for custom evaluation harnesses."""
    shutil.copytree(source, destination, dirs_exist_ok=True)


def _write_fixture_files(root: Path, files: Any) -> None:
    if not isinstance(files, dict):
        raise TypeError("Fixture files must be an object mapping paths to content.")
    for relative, content in files.items():
        if not isinstance(relative, str) or not isinstance(content, str):
            raise TypeError("Fixture paths and contents must be strings.")
        target = _fixture_path(root, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def _fixture_path(root: Path, relative: str) -> Path:
    target = (root / relative).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError:
        raise ValueError(f"Fixture path escapes case root: {relative}") from None
    return target


def render_markdown_report(report: dict[str, Any]) -> str:
    lines = [
        "# RepoAgent Benchmark Report",
        "",
        (
            "> Generated from executable JSONL cases. A passing case requires Agent completion and "
            "all deterministic assertions; a localization case passes when its top-ranked "
            "location names a gold function."
        ),
        "",
        "## Summary",
        "",
        f"- Model: {report.get('model', 'unknown')}",
        f"- Provider model: {', '.join(report.get('provider_models', [])) or 'unknown'}",
        f"- AST tools: {'enabled' if report.get('ast_enabled', True) else 'disabled'}",
        (
            "- Context retrieval: "
            f"{'enabled' if report.get('context_retrieval_enabled', False) else 'disabled'}"
        ),
        f"- AST guidance prompt: {'on' if report.get('ast_guidance') else 'off'}",
        f"- Cases: {report.get('total', 0)}",
        f"- Passed: {report.get('passed', 0)}",
        f"- Pass rate: {float(report.get('pass_rate', 0)):.1%}",
        f"- Average steps: {report.get('average_steps', 0)}",
        f"- Average tool calls: {report.get('average_tool_calls', 0)}",
        f"- Tool errors: {report.get('tool_errors', 0)}",
        f"- Model errors: {report.get('model_errors', 0)}",
        f"- Provider request attempts: {report.get('request_attempts', 0)}",
        f"- JSON repair retries: {report.get('parse_retries', 0)}",
        f"- Locally closed brackets: {report.get('closed_brackets', 0)}",
        f"- AST tool calls: {report.get('ast_tool_calls', 0)}",
        f"- Total tokens: {report.get('total_tokens', 0)}",
        *_localization_summary_lines(report.get("localization")),
        "",
        "## Cases",
        "",
        "| Case | Family | Passed | Status | Steps | Tool calls | Tokens |",
        "|---|---|---:|---|---:|---:|---:|",
    ]
    for result in report.get("results", []):
        metrics = result.get("metrics", {})
        name = str(result.get("name", "unnamed")).replace("|", "\\|")
        lines.append(
            f"| {name} | {result.get('family', 'uncategorized')} | "
            f"{'yes' if result.get('passed') else 'no'} | "
            f"{result.get('status', 'unknown')} | {metrics.get('steps', 0)} | "
            f"{metrics.get('tool_calls', 0)} | {metrics.get('total_tokens', 0)} |"
        )
    errors = [item for item in report.get("results", []) if item.get("status") == "error"]
    if errors:
        lines.extend(["", "## Errors", ""])
        for result in errors:
            name = str(result.get("name", "unnamed"))
            error = str(result.get("error", "unknown error")).replace("\n", " ")
            lines.append(f"- `{name}`: {error}")
    lines.extend(
        [
            "",
            "## Task families",
            "",
            "| Family | Passed | Total | Pass rate |",
            "|---|---:|---:|---:|",
            *[
                f"| {family} | {values['passed']} | {values['total']} | "
                f"{float(values['pass_rate']):.1%} |"
                for family, values in report.get("families", {}).items()
            ],
            "",
            "## Interpretation",
            "",
            (
                "Results depend on the selected model, endpoint, prompt version, and case set. "
                "Do not compare reports unless these inputs are held constant."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def localization_passed(scores: dict[str, Any]) -> bool:
    """Headline rule: the top-ranked location names a gold function.

    File-level accuracy saturates on SWE-bench Lite (every gold patch edits one file), so it only
    decides cases whose gold patch touches no function or class.
    """
    recall = scores.get("function_recall@1")
    return bool(scores.get("file_acc@1")) if recall is None else recall > 0


def _localization_summary_lines(summary: Any) -> list[str]:
    if not isinstance(summary, dict):
        return []
    lines = ["", f"### Localization (n={summary['cases']})", ""]
    ordered = sorted(
        (key for key in summary if key != "cases"),
        key=lambda key: (not key.startswith("function"), key),
    )
    for key in ordered:
        if summary[key] is not None:
            lines.append(f"- {key}: {float(summary[key]):.1%}")
    return lines


def export_predictions(report: dict[str, Any], model_name: str) -> list[dict[str, str]]:
    """SWE-bench prediction records for edit-mode real-repository results."""
    return [
        {
            "instance_id": str(item["instance_id"]),
            "model_name_or_path": model_name,
            "model_patch": str(item.get("model_patch", "")),
        }
        for item in report.get("results", [])
        if "instance_id" in item and "model_patch" in item
    ]
