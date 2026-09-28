"""Aggregate repeated localization runs and compare two conditions with a paired bootstrap.

Each case is first averaged over its runs within a condition; the bootstrap then resamples cases,
so the interval reflects case-to-case variation rather than treating runs as independent cases.
Model or infrastructure errors count as failures (recall 0) and are reported separately.

Usage:
    python scripts/aggregate_runs.py \
        --condition default='reports/full-default-r*.json' \
        --condition guided='reports/full-guided-r*.json' \
        --cases evals/swebench_lite_localize.jsonl --output reports/full-guidance-ablation.md
"""

from __future__ import annotations

import argparse
import glob
import json
import random
import statistics
from pathlib import Path

CASE_METRICS = ("pass", "function_recall@1", "function_recall@5", "file_acc@1")
COST_METRICS = ("steps", "tool_calls", "ast_calls", "tokens")


def case_values(result: dict) -> dict[str, float | None]:
    scores = result.get("localization") or {}
    metrics = result.get("metrics", {})
    counts = metrics.get("tool_counts", {})
    errored = result.get("status") == "error"

    def score(key: str) -> float | None:
        if errored:
            return 0.0
        value = scores.get(key)
        return None if value is None else float(value)

    return {
        "pass": float(bool(result.get("passed"))),
        "function_recall@1": score("function_recall@1"),
        "function_recall@5": score("function_recall@5"),
        "file_acc@1": score("file_acc@1"),
        "steps": float(metrics.get("steps", 0)),
        "tool_calls": float(metrics.get("tool_calls", 0)),
        "ast_calls": float(counts.get("symbol_search", 0) + counts.get("inspect_python", 0)),
        "tokens": float(metrics.get("total_tokens", 0)),
    }


def mean(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    return statistics.fmean(present) if present else None


def load_condition(pattern: str) -> list[dict]:
    paths = sorted(glob.glob(pattern))
    if not paths:
        raise SystemExit(f"No reports match {pattern}")
    return [json.loads(Path(path).read_text(encoding="utf-8")) | {"_path": path} for path in paths]


def per_case(runs: list[dict]) -> dict[str, dict[str, float | None]]:
    """Average each metric per case over the runs that contain the case."""
    collected: dict[str, list[dict[str, float | None]]] = {}
    for run in runs:
        for result in run["results"]:
            collected.setdefault(result["name"], []).append(case_values(result))
    return {
        name: {key: mean([row[key] for row in rows]) for key in rows[0]}
        for name, rows in collected.items()
    }


def paired_bootstrap(
    diffs: list[float], samples: int = 10_000, seed: int = 20261005
) -> tuple[float, float, float]:
    rng = random.Random(seed)
    estimates = sorted(statistics.fmean(rng.choice(diffs) for _ in diffs) for _ in range(samples))
    return statistics.fmean(diffs), estimates[int(0.025 * samples)], estimates[int(0.975 * samples)]


def fmt(key: str, value: float | None) -> str:
    if value is None:
        return "—"
    if key in CASE_METRICS:
        return f"{value:.1%}"
    if key == "tokens":
        return f"{value:,.0f}"
    return f"{value:.2f}"


def fmt_delta(key: str, value: float) -> str:
    if key in CASE_METRICS:
        return f"{value * 100:+.1f} pp"
    if key == "tokens":
        return f"{value:+,.0f}"
    return f"{value:+.2f}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--condition", action="append", required=True, help="name=glob")
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--complete-only",
        action="store_true",
        help="Restrict to cases that finished without error in every run (interim analysis)",
    )
    args = parser.parse_args()

    tiers = {
        case["name"]: case.get("family", "?")
        for case in map(json.loads, args.cases.read_text(encoding="utf-8").splitlines())
    }
    conditions = dict(item.split("=", 1) for item in args.condition)
    runs = {name: load_condition(pattern) for name, pattern in conditions.items()}
    names = list(conditions)
    lines = ["# Repeated-run localization comparison", ""]

    lines += ["## Runs", "", "| Condition | Run | Cases | Errors | Pass | fn recall@1 | Tokens |"]
    lines += ["|---|---|---:|---:|---:|---:|---:|"]
    for name in names:
        for run in runs[name]:
            results = run["results"]
            errors = sum(item.get("status") == "error" for item in results)
            recall = mean([case_values(item)["function_recall@1"] for item in results])
            lines.append(
                f"| {name} | {Path(run['_path']).stem} | {len(results)} | {errors} | "
                f"{sum(bool(item.get('passed')) for item in results)} | "
                f"{fmt('function_recall@1', recall)} | {run.get('total_tokens', 0):,} |"
            )
        lines.append(
            f"| {name} | recoveries | | | | | closed brackets "
            f"{sum(run.get('closed_brackets', 0) for run in runs[name])}, JSON repairs "
            f"{sum(run.get('parse_retries', 0) for run in runs[name])} |"
        )

    averaged = {name: per_case(runs[name]) for name in names}
    shared = sorted(set.intersection(*(set(values) for values in averaged.values())))
    scope = "shared cases"
    if args.complete_only:
        errored = {
            item["name"]
            for name in names
            for run in runs[name]
            for item in run["results"]
            if item.get("status") == "error"
        }
        shared = [case for case in shared if case not in errored]
        scope = "cases without errors in any run (interim; excludes errored cases)"
    lines += ["", f"## Per-condition means over {len(shared)} {scope}", ""]
    lines += ["| Metric | " + " | ".join(names) + " | Run range (" + " / ".join(names) + ") |"]
    lines += ["|---|" + "---:|" * len(names) + "---|"]
    for key in (*CASE_METRICS, *COST_METRICS):
        cells = [fmt(key, mean([averaged[name][case][key] for case in shared])) for name in names]
        ranges = []
        for name in names:
            per_run = [
                mean([case_values(item)[key] for item in run["results"] if item["name"] in shared])
                for run in runs[name]
            ]
            present = [value for value in per_run if value is not None]
            ranges.append(f"{fmt(key, min(present))}–{fmt(key, max(present))}" if present else "—")
        lines.append(f"| {key} | " + " | ".join(cells) + " | " + " / ".join(ranges) + " |")

    if len(names) == 2:
        base, cand = names
        lines += ["", f"## Paired difference: {cand} − {base} (bootstrap over cases, 95% CI)", ""]
        groups = {"all": shared}
        for tier in ("small", "medium", "large"):
            groups[tier] = [case for case in shared if tiers.get(case) == tier]
        lines += [
            "| Metric | "
            + " | ".join(f"{group} (n={len(cases)})" for group, cases in groups.items())
            + " |"
        ]
        lines += ["|---|" + "---|" * len(groups)]
        for key in (*CASE_METRICS, *COST_METRICS):
            cells = []
            for cases in groups.values():
                diffs = [
                    averaged[cand][case][key] - averaged[base][case][key]
                    for case in cases
                    if averaged[cand][case][key] is not None
                    and averaged[base][case][key] is not None
                ]
                if not diffs:
                    cells.append("—")
                    continue
                point, low, high = paired_bootstrap(diffs)
                cells.append(
                    f"{fmt_delta(key, point)} [{fmt_delta(key, low)}, {fmt_delta(key, high)}]"
                )
            lines.append(f"| {key} | " + " | ".join(cells) + " |")
        lines += [
            "",
            (
                "An interval that excludes zero indicates a difference larger than case-to-case "
                "variation in this suite; it does not generalize beyond these cases, this model, "
                "or this prompt version."
            ),
        ]

    text = "\n".join(lines) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
