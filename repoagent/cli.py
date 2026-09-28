from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

from . import __version__
from .agent import RepositoryAgent
from .comparison import compare_reports, render_comparison_markdown
from .config import AgentConfig
from .demo import run_demo
from .evals import (
    evaluate_case,
    export_predictions,
    load_cases,
    merge_benchmark_reports,
    render_markdown_report,
)
from .llm import OpenAICompatibleClient
from .metrics import aggregate_results
from .runstore import history_report
from .tools import ToolError, restore_run


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="repoagent", description="Safe repository maintenance agent"
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run = subparsers.add_parser("run", help="Plan or execute a repository maintenance task")
    run.add_argument("task", help="Natural-language maintenance task")
    run.add_argument("--root", default=".", help="Repository root")
    run.add_argument("--model", help="Model name; defaults to REPO_AGENT_MODEL")
    run.add_argument("--base-url", help="OpenAI-compatible API base URL")
    run.add_argument("--api-key", help="API key; prefer REPO_AGENT_API_KEY")
    run.add_argument("--apply", action="store_true", help="Allow guarded file writes")
    run.add_argument(
        "--allow-checks",
        action="store_true",
        help="Allow execution of allowlisted test/lint commands from the repository",
    )
    run.add_argument("--max-steps", type=int, default=18)
    run.add_argument("--disable-ast", action="store_true", help="Disable Python AST tools")
    run.add_argument(
        "--disable-context", action="store_true", help="Disable ranked context retrieval"
    )
    run.add_argument("--json", action="store_true", help="Print machine-readable result")

    evaluate = subparsers.add_parser("eval", help="Run JSONL benchmark cases in temporary repos")
    evaluate.add_argument("cases", type=Path)
    evaluate.add_argument("--model", help="Model name; defaults to REPO_AGENT_MODEL")
    evaluate.add_argument("--base-url", help="OpenAI-compatible API base URL")
    evaluate.add_argument("--api-key", help="API key; prefer REPO_AGENT_API_KEY")
    evaluate.add_argument("--limit", type=int)
    evaluate.add_argument(
        "--case", action="append", dest="case_names", help="Run only a named case"
    )
    evaluate.add_argument("--disable-ast", action="store_true", help="Run string-search baseline")
    evaluate.add_argument(
        "--disable-context", action="store_true", help="Disable ranked context retrieval"
    )
    evaluate.add_argument("--max-steps", type=int, default=18)
    evaluate.add_argument(
        "--ast-guidance",
        action="store_true",
        help="Add an AST-first workflow to the localization prompt",
    )
    evaluate.add_argument(
        "--predictions",
        type=Path,
        help="Write SWE-bench prediction JSONL for edit-mode real-repository cases",
    )
    evaluate.add_argument("--output", type=Path, help="Write the full JSON report")
    evaluate.add_argument(
        "--markdown", type=Path, help="Write a portfolio-friendly Markdown report"
    )
    evaluate.add_argument("--artifacts", type=Path, help="Preserve failed case repos and traces")
    evaluate.add_argument(
        "--resume",
        action="store_true",
        help="Reuse completed cases from --output and retry interrupted/error cases",
    )
    evaluate.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue remaining cases after an infrastructure or model error",
    )

    restore = subparsers.add_parser("restore", help="Restore files changed by a previous run")
    restore.add_argument("run_id")
    restore.add_argument("--root", default=".", help="Repository root")

    demo = subparsers.add_parser(
        "demo", help="Run a deterministic end-to-end demo without an API key"
    )
    demo.add_argument(
        "--output", type=Path, help="Empty destination; defaults to a new temporary directory"
    )
    demo.add_argument("--json", action="store_true")

    report = subparsers.add_parser("report", help="Summarize stored run metrics")
    report.add_argument("--root", default=".", help="Repository root")
    report.add_argument("--json", action="store_true")

    compare = subparsers.add_parser("compare", help="Compare two benchmark JSON reports")
    compare.add_argument("baseline", type=Path)
    compare.add_argument("candidate", type=Path)
    compare.add_argument("--output", type=Path, help="Write Markdown comparison")

    merge = subparsers.add_parser("merge", help="Replace retried cases in a benchmark report")
    merge.add_argument("base", type=Path)
    merge.add_argument("update", type=Path)
    merge.add_argument("--output", type=Path, required=True, help="Write merged JSON report")
    merge.add_argument("--markdown", type=Path, help="Write merged Markdown report")
    return parser


def _config(args: argparse.Namespace, root: str | Path, apply_changes: bool) -> AgentConfig:
    return AgentConfig.from_env(
        root,
        model=args.model,
        api_key=args.api_key,
        base_url=args.base_url,
        apply_changes=apply_changes,
        allow_checks=getattr(args, "allow_checks", False),
        enable_ast_tools=not getattr(args, "disable_ast", False),
        enable_context_retrieval=not getattr(args, "disable_context", False),
        max_steps=getattr(args, "max_steps", 18),
        ast_guidance=getattr(args, "ast_guidance", False),
    )


def _benchmark_report(config: AgentConfig, results: list[dict[str, object]]) -> dict[str, object]:
    return {
        "model": config.model,
        "ast_enabled": config.enable_ast_tools,
        "context_retrieval_enabled": config.enable_context_retrieval,
        "ast_guidance": config.ast_guidance,
        **aggregate_results(results),
        "results": results,
    }


def _write_benchmark_report(
    report: dict[str, object], output: Path | None, markdown: Path | None
) -> None:
    if output:
        _atomic_write(
            output,
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        )
    if markdown:
        _atomic_write(markdown, render_markdown_report(report))


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "restore":
            restored = restore_run(Path(args.root), args.run_id)
            print("Restored: " + (", ".join(restored) if restored else "no files"))
            return 0
        if args.command == "demo":
            destination = args.output or Path(tempfile.mkdtemp(prefix="repoagent-demo-"))
            result = run_demo(destination)
            if args.json:
                print(
                    json.dumps(
                        {"repository": str(destination), **result.to_dict()},
                        ensure_ascii=False,
                        indent=2,
                    )
                )
            else:
                print(f"Demo repository: {destination}")
                print(f"Status: {result.status} — {result.summary}")
                print(f"Trace: {result.trace_path}")
                print(json.dumps(result.metrics, ensure_ascii=False, indent=2))
                print(result.diff)
            return 0 if result.status == "completed" else 1
        if args.command == "report":
            report = history_report(Path(args.root))
            if args.json:
                print(json.dumps(report, ensure_ascii=False, indent=2))
            else:
                print(f"Runs: {report['total_runs']}")
                print(f"Completion rate: {report['completion_rate']:.1%}")
                print(f"Tool calls/errors: {report['tool_calls']}/{report['tool_errors']}")
                print(f"Changed files: {report['changed_files']}")
                print(f"Total tokens: {report['total_tokens']}")
            return 0
        if args.command == "compare":
            baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
            candidate = json.loads(args.candidate.read_text(encoding="utf-8"))
            comparison = compare_reports(baseline, candidate)
            markdown = render_comparison_markdown(comparison)
            if args.output:
                args.output.parent.mkdir(parents=True, exist_ok=True)
                args.output.write_text(markdown, encoding="utf-8")
            print(markdown)
            return 0
        if args.command == "merge":
            base = json.loads(args.base.read_text(encoding="utf-8"))
            update = json.loads(args.update.read_text(encoding="utf-8"))
            merged = merge_benchmark_reports(base, update)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            if args.markdown:
                args.markdown.parent.mkdir(parents=True, exist_ok=True)
                args.markdown.write_text(render_markdown_report(merged), encoding="utf-8")
            print(json.dumps(merged, ensure_ascii=False, indent=2))
            return 0
        if args.command == "run":
            result = RepositoryAgent(_config(args, args.root, args.apply)).run(args.task)
            if args.json:
                print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
            else:
                mode = "APPLY" if args.apply else "PREVIEW"
                print(f"[{mode}] {result.status}: {result.summary}")
                print(f"Run: {result.run_id}")
                print(f"Trace: {result.trace_path}")
                if result.changed_files:
                    print("Changed: " + ", ".join(result.changed_files))
                if result.diff:
                    print(result.diff)
            return 0 if result.status == "completed" else 2

        config = _config(args, ".", True)
        client = OpenAICompatibleClient(
            model=config.model, api_key=config.api_key, base_url=config.base_url
        )
        cases = load_cases(args.cases)
        if args.case_names:
            selected = set(args.case_names)
            available = {str(case.get("name")) for case in cases}
            missing = selected - available
            if missing:
                raise ValueError(f"Unknown benchmark cases: {', '.join(sorted(missing))}")
            cases = [case for case in cases if case.get("name") in selected]
        if args.limit is not None:
            cases = cases[: max(0, args.limit)]
        if args.artifacts:
            args.artifacts.mkdir(parents=True, exist_ok=True)
        results: list[dict[str, object]] = []
        if args.resume:
            if args.output is None:
                raise ValueError("--resume requires --output.")
            if args.output.exists():
                previous = json.loads(args.output.read_text(encoding="utf-8"))
                if not isinstance(previous, dict):
                    raise ValueError("Cannot resume: existing output is not a JSON object.")
                if previous.get("model") != config.model:
                    raise ValueError("Cannot resume a report created with a different model.")
                if previous.get("ast_enabled") != config.enable_ast_tools:
                    raise ValueError("Cannot resume a report with a different AST configuration.")
                if (
                    previous.get("context_retrieval_enabled", False)
                    != config.enable_context_retrieval
                ):
                    raise ValueError(
                        "Cannot resume a report with a different context-retrieval configuration."
                    )
                if bool(previous.get("ast_guidance")) != config.ast_guidance:
                    raise ValueError("Cannot resume a report with a different AST guidance prompt.")
                selected_names = {
                    str(case.get("name", case.get("task", "unnamed"))) for case in cases
                }
                results = [
                    item
                    for item in previous.get("results", [])
                    if isinstance(item, dict)
                    and item.get("name") in selected_names
                    and item.get("status") != "error"
                ]
                completed_names = {str(item.get("name")) for item in results}
                cases = [
                    case
                    for case in cases
                    if str(case.get("name", case.get("task", "unnamed"))) not in completed_names
                ]
        total_cases = len(results) + len(cases)
        for index, case in enumerate(cases, len(results) + 1):
            name = str(case.get("name", case.get("task", "unnamed")))
            print(f"[{index}/{total_cases}] running {name}", file=sys.stderr, flush=True)
            result = evaluate_case(case, config, client, args.artifacts)
            results.append(result)
            report = _benchmark_report(config, results)
            _write_benchmark_report(report, args.output, args.markdown)
            print(
                f"[{index}/{total_cases}] {name}: {result.get('status')} "
                f"({'pass' if result.get('passed') else 'fail'})",
                file=sys.stderr,
                flush=True,
            )
            if result.get("status") == "error" and not args.continue_on_error:
                print(f"repoagent: {result.get('error')}", file=sys.stderr)
                break
        report = _benchmark_report(config, results)
        _write_benchmark_report(report, args.output, args.markdown)
        if args.predictions:
            _atomic_write(
                args.predictions,
                "".join(
                    json.dumps(item, ensure_ascii=False) + "\n"
                    for item in export_predictions(report, config.model)
                ),
            )
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if any(item.get("status") == "error" for item in results):
            return 2
        return 0 if report["passed"] == report["total"] else 1
    except (TypeError, ValueError, RuntimeError, OSError, ToolError) as exc:
        print(f"repoagent: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
