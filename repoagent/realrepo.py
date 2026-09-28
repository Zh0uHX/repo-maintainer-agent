"""Real-repository evaluation support: cached clones, gold locations, and localization scoring.

A real-repository case replaces inline ``files`` with ``repo`` + ``base_commit``. The workspace is
materialized with ``git archive`` so the Agent never sees a ``.git`` directory or later history.
"""

from __future__ import annotations

import ast
import os
import re
import subprocess
import tarfile
import warnings
from pathlib import Path
from typing import Any

DEFAULT_CACHE = Path(os.getenv("REPOAGENT_REPO_CACHE", "~/.cache/repoagent-repos")).expanduser()
_REPO_PATTERN = re.compile(r"(?!\.)[A-Za-z0-9_.-]+/(?!\.)[A-Za-z0-9_.-]+")
_COMMIT_PATTERN = re.compile(r"[0-9a-f]{7,40}")
_HUNK_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+\d+(?:,\d+)? @@")


def _git(args: list[str], cwd: Path | None = None) -> str:
    completed = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {completed.stderr.strip()[:500]}")
    return completed.stdout


def cached_clone(repo: str, cache_dir: Path = DEFAULT_CACHE) -> Path:
    """Return a bare, blob-less clone of ``owner/name``, cloning it on first use."""
    if not _REPO_PATTERN.fullmatch(repo):
        raise ValueError(f"Invalid repository name: {repo}")
    destination = cache_dir / (repo.replace("/", "__") + ".git")
    if not destination.exists():
        cache_dir.mkdir(parents=True, exist_ok=True)
        partial = destination.with_suffix(".partial")
        _git(
            [
                "clone",
                "--bare",
                "--filter=blob:none",
                f"https://github.com/{repo}.git",
                str(partial),
            ]
        )
        partial.rename(destination)
    return destination


def materialize(repo: str, base_commit: str, root: Path, cache_dir: Path = DEFAULT_CACHE) -> None:
    """Extract the tree at ``base_commit`` into ``root`` without Git metadata."""
    if not _COMMIT_PATTERN.fullmatch(base_commit):
        raise ValueError(f"Invalid base commit: {base_commit}")
    clone = cached_clone(repo, cache_dir)
    process = subprocess.Popen(
        ["git", "archive", "--format=tar", base_commit],
        cwd=clone,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert process.stdout is not None
    with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
        archive.extractall(root, filter="data")
    _, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"git archive {base_commit} failed: {stderr.decode()[:500]}")


def python_file_count(repo: str, base_commit: str, cache_dir: Path = DEFAULT_CACHE) -> int:
    listing = _git(["ls-tree", "-r", "--name-only", base_commit], cwd=cached_clone(repo, cache_dir))
    return sum(1 for line in listing.splitlines() if line.endswith(".py"))


def patch_files(patch: str) -> list[str]:
    return re.findall(r"^diff --git a/(\S+) b/", patch, re.MULTILINE)


def changed_old_lines(patch: str) -> dict[str, list[int]]:
    """Map each patched file to pre-image line numbers that the patch removes or inserts at."""
    result: dict[str, list[int]] = {}
    current: list[int] | None = None
    old_line = 0
    for line in patch.splitlines():
        if line.startswith("diff --git "):
            files = patch_files(line + "\n")
            current = result.setdefault(files[0], []) if files else None
            continue
        header = _HUNK_HEADER.match(line)
        if header:
            old_line = int(header.group(1))
            continue
        if current is None or line.startswith(("---", "+++")):
            continue
        if line.startswith("-"):
            current.append(old_line)
            old_line += 1
        elif line.startswith("+"):
            # Insertions touch the scope that encloses the preceding pre-image line.
            current.append(max(old_line - 1, 1))
        elif line.startswith(" "):
            old_line += 1
    return {path: sorted(set(lines)) for path, lines in result.items()}


def enclosing_symbols(source: str, lines: list[int]) -> list[str]:
    """Return qualified names of the innermost function or class enclosing each line."""
    with warnings.catch_warnings():
        # Historical sources often contain invalid escape sequences that only warn.
        warnings.simplefilter("ignore", SyntaxWarning)
        tree = ast.parse(source)
    spans: list[tuple[int, int, str]] = []

    def visit(node: ast.AST, scope: list[str]) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                qualified = ".".join([*scope, child.name])
                start = min([child.lineno, *(d.lineno for d in child.decorator_list)])
                spans.append((start, child.end_lineno or child.lineno, qualified))
                visit(child, [*scope, child.name])
            else:
                visit(child, scope)

    visit(tree, [])
    found: list[str] = []
    for line in lines:
        containing = [span for span in spans if span[0] <= line <= span[1]]
        if containing:
            innermost = min(containing, key=lambda span: span[1] - span[0])
            if innermost[2] not in found:
                found.append(innermost[2])
    return found


def gold_locations(
    repo: str, base_commit: str, patch: str, cache_dir: Path = DEFAULT_CACHE
) -> dict[str, Any]:
    """Derive gold files and enclosing symbols from a reference patch at ``base_commit``."""
    clone = cached_clone(repo, cache_dir)
    functions: list[dict[str, str]] = []
    for path, lines in changed_old_lines(patch).items():
        if not path.endswith(".py"):
            continue
        try:
            source = _git(["show", f"{base_commit}:{path}"], cwd=clone)
        except RuntimeError:
            continue  # File created by the patch: only the file-level target applies.
        try:
            symbols = enclosing_symbols(source, lines)
        except SyntaxError:
            continue
        functions.extend({"path": path, "symbol": symbol} for symbol in symbols)
    return {"files": patch_files(patch), "functions": functions}


def _symbol_matches(predicted: str, gold: str) -> bool:
    """Accept exact names and a method predicted without, or with a longer, class prefix."""
    if not predicted:
        return False
    return predicted == gold or gold.endswith("." + predicted) or predicted.endswith("." + gold)


def score_localization(
    predicted: list[dict[str, str]], gold: dict[str, Any], ks: tuple[int, ...] = (1, 3, 5)
) -> dict[str, Any]:
    """File Acc@k: any gold file in the top-k distinct predicted files.

    Function recall@k: share of gold symbols matched within the top-k predictions.
    """
    ranked_files: list[str] = []
    for item in predicted:
        if item["path"] not in ranked_files:
            ranked_files.append(item["path"])
    gold_files = set(gold.get("files", []))
    gold_functions = gold.get("functions", [])
    scores: dict[str, Any] = {}
    for k in ks:
        scores[f"file_acc@{k}"] = bool(gold_files & set(ranked_files[:k]))
        top = predicted[:k]
        if gold_functions:
            hits = sum(
                any(
                    item["path"] == target["path"]
                    and _symbol_matches(item.get("symbol", ""), target["symbol"])
                    for item in top
                )
                for target in gold_functions
            )
            scores[f"function_recall@{k}"] = round(hits / len(gold_functions), 4)
        else:
            scores[f"function_recall@{k}"] = None
    scores["predicted_files"] = ranked_files
    return scores
