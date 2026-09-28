"""Select a stratified real-repository evaluation suite from SWE-bench Lite.

Every SWE-bench Lite gold patch edits exactly one file with at most three hunks, so task
families such as cross-file refactors cannot be drawn from it. Cases are instead stratified by
repository size (Python files at ``base_commit``) and by patch hunk count.

Usage:
    python scripts/select_cases.py --output evals/swebench_lite_localize.jsonl
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from repoagent.realrepo import gold_locations, python_file_count

ROWS_URL = (
    "https://datasets-server.huggingface.co/rows?dataset=princeton-nlp%2FSWE-bench_Lite"
    "&config=default&split=test&offset={offset}&length=100"
)
TIERS = (("small", 0, 150), ("medium", 150, 800), ("large", 800, 10**9))


def load_lite(source: Path | None) -> list[dict]:
    if source is not None:
        return json.loads(source.read_text(encoding="utf-8"))
    rows: list[dict] = []
    for offset in range(0, 300, 100):
        with urllib.request.urlopen(ROWS_URL.format(offset=offset), timeout=60) as response:
            rows.extend(item["row"] for item in json.load(response)["rows"])
    return rows


def tier_of(count: int) -> str:
    return next(name for name, low, high in TIERS if low <= count < high)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--lite", type=Path, help="Local JSON list of SWE-bench Lite rows")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--per-tier", type=int, default=15)
    parser.add_argument("--max-per-repo", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20261005)
    parser.add_argument("--mode", choices=("localize", "edit"), default="localize")
    args = parser.parse_args()

    rows = load_lite(args.lite)
    by_tier: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        count = python_file_count(row["repo"], row["base_commit"])
        row["_py_files"] = count
        row["_hunks"] = len(re.findall(r"^@@", row["patch"], re.MULTILINE))
        by_tier[tier_of(count)].append(row)

    rng = random.Random(args.seed)
    selected: list[dict] = []
    for name, _, _ in TIERS:
        pool = sorted(by_tier[name], key=lambda row: row["instance_id"])
        rng.shuffle(pool)
        # Round-robin over hunk counts so multi-hunk patches are not crowded out.
        buckets: dict[int, list[dict]] = defaultdict(list)
        for row in pool:
            buckets[row["_hunks"]].append(row)
        per_repo: Counter[str] = Counter()
        chosen: list[dict] = []
        while len(chosen) < args.per_tier and any(buckets.values()):
            for hunks in sorted(buckets):
                while buckets[hunks]:
                    row = buckets[hunks].pop()
                    if per_repo[row["repo"]] < args.max_per_repo:
                        per_repo[row["repo"]] += 1
                        chosen.append(row)
                        break
                if len(chosen) >= args.per_tier:
                    break
        selected.extend(chosen)
        print(
            f"{name}: {len(chosen)}/{len(pool)} selected, repos={dict(per_repo)}",
            file=sys.stderr,
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as stream:
        for row in selected:
            tier = tier_of(row["_py_files"])
            case = {
                "name": row["instance_id"],
                "instance_id": row["instance_id"],
                "family": tier,
                "mode": args.mode,
                "repo": row["repo"],
                "base_commit": row["base_commit"],
                "task": row["problem_statement"],
                "gold": gold_locations(row["repo"], row["base_commit"], row["patch"]),
                "meta": {"python_files": row["_py_files"], "hunks": row["_hunks"]},
            }
            stream.write(json.dumps(case, ensure_ascii=False) + "\n")
    print(f"wrote {len(selected)} cases to {args.output}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
