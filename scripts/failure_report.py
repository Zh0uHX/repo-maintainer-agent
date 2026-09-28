"""Label localization results with deterministic failure categories.

Categories, checked in order:
    protocol     model request failed (malformed JSON after repairs, provider error)
    step_budget  Agent never finished within max_steps
    tool_errors  stopped after four consecutive rejected actions
    gave_up      Agent finished with needs_input or failed
    wrong_file   gold file absent from the top-5 predicted files
    ranking      gold file in the top-5 but not ranked first
    wrong_symbol gold file ranked first but no gold function in the top-1 prediction
    pass         gold file first and (when gold functions exist) top-1 function correct

Also reports the first step whose observation mentions a gold file, which separates "never found
the code" from "found it and then ranked something else first".

Usage:
    python scripts/failure_report.py reports/run.json evals/suite.jsonl --artifacts reports/run-artifacts
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


def label(result: dict, trace_summary: str = "") -> str:
    if result.get("status") == "error":
        return "protocol"
    summary = str(result.get("summary") or trace_summary).lower()
    if "step budget" in summary:
        return "step_budget"
    if "consecutive invalid" in summary:
        return "tool_errors"
    scores = result.get("localization")
    if result.get("status") != "completed" or not isinstance(scores, dict):
        return "gave_up"
    if not scores.get("file_acc@5"):
        return "wrong_file"
    if not scores.get("file_acc@1"):
        return "ranking"
    recall = scores.get("function_recall@1")
    if recall is not None and recall == 0:
        return "wrong_symbol"
    return "pass"


def read_trace(trace: Path, gold_files: list[str]) -> tuple[int | None, str]:
    """Return the first step mentioning a gold file and an inferred stop reason.

    Reports written before results carried ``summary`` need the stop reason from the trace.
    """
    touch = None
    finished = False
    oks: list[bool] = []
    for line in trace.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("event") == "finish":
            finished = True
        if record.get("event") != "tool_observation":
            continue
        oks.append(bool(record["payload"].get("ok")))
        body = json.dumps(record["payload"].get("result", ""), ensure_ascii=False)
        if touch is None and any(path in body for path in gold_files):
            touch = int(record["payload"]["step"])
    if finished:
        reason = ""
    elif len(oks) >= 4 and not any(oks[-4:]):
        reason = "consecutive invalid"
    else:
        reason = "step budget"
    return touch, reason


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("report", type=Path)
    parser.add_argument("cases", type=Path)
    parser.add_argument("--artifacts", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = json.loads(args.report.read_text(encoding="utf-8"))
    cases = {
        case["name"]: case
        for case in map(json.loads, args.cases.read_text(encoding="utf-8").splitlines())
    }
    rows = []
    for result in report["results"]:
        case = cases.get(result["name"], {})
        gold = case.get("gold", {})
        touch, trace_summary = None, ""
        if args.artifacts:
            safe = re.sub(r"[^A-Za-z0-9_.-]+", "-", result["name"]).strip("-")
            traces = sorted((args.artifacts / safe).glob("runs/*/trace.jsonl"))
            if traces:
                touch, trace_summary = read_trace(traces[-1], gold.get("files", []))
        metrics = result.get("metrics", {})
        predicted = (result.get("locations") or [{}])[0]
        rows.append(
            {
                "name": result["name"],
                "tier": case.get("family", "?"),
                "label": label(result, trace_summary),
                "steps": metrics.get("steps", 0),
                "first_gold_touch": touch,
                "tokens": metrics.get("total_tokens", 0),
                "ast_calls": sum(
                    metrics.get("tool_counts", {}).get(name, 0)
                    for name in ("symbol_search", "inspect_python")
                ),
                "top1": f"{predicted.get('path', '')}::{predicted.get('symbol', '')}".strip(":"),
                "gold": "; ".join(
                    f"{item['path']}::{item['symbol']}" for item in gold.get("functions", [])
                )
                or "; ".join(gold.get("files", [])),
            }
        )

    counts = Counter(row["label"] for row in rows)
    lines = [
        f"# Failure breakdown: {args.report.name}",
        "",
        f"Model: {report.get('model')} · cases: {len(rows)} · "
        + " · ".join(f"{name} {count}" for name, count in counts.most_common()),
        "",
        "| Case | Tier | Label | Steps | First gold touch | AST calls | Tokens | Top-1 | Gold |",
        "|---|---|---|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['name']} | {row['tier']} | {row['label']} | {row['steps']} | "
            f"{row['first_gold_touch'] if row['first_gold_touch'] is not None else '—'} | "
            f"{row['ast_calls']} | {row['tokens']} | `{row['top1']}` | `{row['gold']}` |"
        )
    text = "\n".join(lines) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
