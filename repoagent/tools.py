from __future__ import annotations

import difflib
import fnmatch
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from .config import AgentConfig
from .indexing import inspect_python_file, iter_python_files
from .retrieval import query_terms, rank_repository_context
from .runstore import safe_runs_dir

SKIP_DIRS = {
    ".git",
    ".repoagent",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
}
SENSITIVE_NAMES = {
    ".env",
    ".env.local",
    "id_rsa",
    "id_ed25519",
    "credentials.json",
    "secrets.json",
}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
MAX_CONTEXT_FILES = 240
MAX_CONTEXT_INDEX_BYTES = 8_000_000


def _is_sensitive_name(name: str) -> bool:
    lowered = name.lower()
    return (
        lowered in SENSITIVE_NAMES
        or lowered.startswith(".env")
        or Path(lowered).suffix in SENSITIVE_SUFFIXES
    )


class ToolError(RuntimeError):
    pass


class RepositoryTools:
    def __init__(self, config: AgentConfig, run_dir: Path) -> None:
        self.config = config
        self.root = config.root.resolve()
        self.run_dir = run_dir
        self.backup_dir = run_dir / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.changed_files: set[str] = set()
        self.checks: list[dict[str, Any]] = []
        self._originally_missing: set[str] = set()
        self._previews: list[str] = []
        self._symbol_cache: dict[str, tuple[int, int, dict[str, Any]]] = {}

    def execute(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        dispatch = {
            "list_files": self.list_files,
            "read_file": self.read_file,
            "search": self.search,
        }
        if self.config.task_mode == "edit":
            dispatch.update(
                {
                    "edit_file": self.edit_file,
                    "write_file": self.write_file,
                    "run_check": self.run_check,
                    "diff": self.diff,
                }
            )
        if self.config.enable_ast_tools:
            dispatch.update(
                {
                    "inspect_python": self.inspect_python,
                    "symbol_search": self.symbol_search,
                }
            )
        if self.config.enable_context_retrieval:
            dispatch["retrieve_context"] = self.retrieve_context
        if name not in dispatch:
            raise ToolError(f"Unknown tool: {name}")
        try:
            return dispatch[name](**args)
        except TypeError as exc:
            raise ToolError(f"Invalid arguments for {name}: {exc}") from exc

    def _resolve(self, relative: str, *, allow_missing: bool = False) -> Path:
        if not isinstance(relative, str) or not relative or "\x00" in relative:
            raise ToolError("Path must be a non-empty string.")
        candidate = (self.root / relative).resolve(strict=False)
        try:
            rel = candidate.relative_to(self.root)
        except ValueError:
            raise ToolError("Path escapes repository root.") from None
        if any(part in SKIP_DIRS for part in rel.parts) or _is_sensitive_name(candidate.name):
            raise ToolError("Path is protected or excluded.")
        if not allow_missing and not candidate.exists():
            raise ToolError(f"Path does not exist: {relative}")
        if candidate.exists() and candidate.is_symlink():
            raise ToolError("Symbolic links are not writable/readable by the agent.")
        return candidate

    def _read_text(self, path: Path) -> str:
        if not path.is_file():
            raise ToolError("Path is not a file.")
        if path.stat().st_size > self.config.max_file_bytes:
            raise ToolError(f"File exceeds {self.config.max_file_bytes} byte limit.")
        data = path.read_bytes()
        if b"\x00" in data[:4096]:
            raise ToolError("Binary files are not supported.")
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            raise ToolError("File is not valid UTF-8.") from None

    def list_files(self, pattern: str = "*", limit: int = 200) -> dict[str, Any]:
        limit = max(1, min(int(limit), 1000))
        files: list[str] = []
        for current, dirs, names in os.walk(self.root):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            for name in sorted(names):
                path = Path(current) / name
                rel = path.relative_to(self.root).as_posix()
                if _is_sensitive_name(name) or path.is_symlink():
                    continue
                if fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(name, pattern):
                    files.append(rel)
                    if len(files) >= limit:
                        return {"files": files, "truncated": True}
        return {"files": files, "truncated": False}

    def read_file(self, path: str, start_line: int = 1, end_line: int = 240) -> dict[str, Any]:
        target = self._resolve(path)
        text = self._read_text(target)
        lines = text.splitlines()
        start = max(1, int(start_line))
        end = max(start, min(int(end_line), start + 499))
        selected = [f"{idx}: {lines[idx - 1]}" for idx in range(start, min(end, len(lines)) + 1)]
        return {
            "path": path,
            "content": "\n".join(selected),
            "total_lines": len(lines),
            "truncated": end < len(lines),
        }

    def search(
        self,
        query: str,
        glob: str = "*",
        regex: bool = False,
        limit: int = 80,
    ) -> dict[str, Any]:
        if not query:
            raise ToolError("Search query cannot be empty.")
        try:
            matcher = re.compile(query) if regex else None
        except re.error as exc:
            raise ToolError(f"Invalid regex: {exc}") from exc
        matches: list[dict[str, Any]] = []
        for relative in self.list_files(glob, 1000)["files"]:
            try:
                text = self._read_text(self._resolve(relative))
            except ToolError:
                continue
            for number, line in enumerate(text.splitlines(), 1):
                found = bool(matcher.search(line)) if matcher else query in line
                if found:
                    matches.append({"path": relative, "line": number, "text": line[:500]})
                    if len(matches) >= min(max(1, int(limit)), 200):
                        return {"matches": matches, "truncated": True}
        return {"matches": matches, "truncated": False}

    def inspect_python(self, path: str) -> dict[str, Any]:
        target = self._resolve(path)
        if target.suffix != ".py":
            raise ToolError("inspect_python only supports Python source files.")
        return self._inspect_cached(target, path)

    def _inspect_cached(self, target: Path, relative: str) -> dict[str, Any]:
        """Parse a Python file once per (mtime, size); edits invalidate the entry."""
        stat = target.stat()
        cached = self._symbol_cache.get(relative)
        if cached and cached[0] == stat.st_mtime_ns and cached[1] == stat.st_size:
            return cached[2]
        result = inspect_python_file(target, relative, self.config.max_file_bytes)
        self._symbol_cache[relative] = (stat.st_mtime_ns, stat.st_size, result)
        return result

    def repository_overview(self, max_entries: int = 60) -> dict[str, Any]:
        """Summarize directories by file count so large repositories fit in the plan prompt."""
        counts: dict[str, int] = {}
        top_files: list[str] = []
        total = 0
        for current, dirs, names in os.walk(self.root):
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS)
            rel_dir = Path(current).relative_to(self.root)
            for name in names:
                if _is_sensitive_name(name) or (Path(current) / name).is_symlink():
                    continue
                total += 1
                if not rel_dir.parts:
                    top_files.append(name)
                    continue
                key = "/".join(rel_dir.parts[:2])
                counts[key] = counts.get(key, 0) + 1
        ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:max_entries]
        return {
            "total_files": total,
            "top_level_files": sorted(top_files)[:max_entries],
            "directories": {path: count for path, count in sorted(ranked)},
            "truncated": len(counts) > max_entries or len(top_files) > max_entries,
        }

    def symbol_search(self, name: str, kind: str = "", limit: int = 80) -> dict[str, Any]:
        if not name:
            raise ToolError("Symbol name cannot be empty.")
        normalized_name = name.casefold()
        normalized_kind = kind.casefold()
        matches: list[dict[str, Any]] = []
        parse_errors: list[dict[str, str]] = []
        for path in iter_python_files(self.root, SKIP_DIRS):
            relative = path.relative_to(self.root).as_posix()
            result = self._inspect_cached(path, relative)
            if result["error"]:
                parse_errors.append({"path": relative, "error": result["error"]})
                continue
            for symbol in result["symbols"]:
                if normalized_name not in symbol["qualified_name"].casefold():
                    continue
                if normalized_kind and normalized_kind != symbol["kind"].casefold():
                    continue
                matches.append(symbol)
                if len(matches) >= min(max(1, int(limit)), 200):
                    return {
                        "matches": matches,
                        "parse_errors": parse_errors[:20],
                        "truncated": True,
                    }
        return {"matches": matches, "parse_errors": parse_errors[:20], "truncated": False}

    def retrieve_context(self, query: str, glob: str = "*", limit: int = 8) -> dict[str, Any]:
        if not isinstance(query, str) or not query.strip():
            raise ToolError("Context query cannot be empty.")
        if len(query) > 2_000:
            raise ToolError("Context query exceeds the 2000 character limit.")
        try:
            selected_limit = max(1, min(int(limit), 12))
        except (TypeError, ValueError):
            raise ToolError("Context result limit must be an integer.") from None
        terms = query_terms(query)
        if not terms:
            raise ToolError("Context query does not contain searchable terms.")
        documents: list[dict[str, Any]] = []
        parse_errors: list[dict[str, str]] = []
        listing = self.list_files(glob, MAX_CONTEXT_FILES + 1)
        paths = listing["files"][:MAX_CONTEXT_FILES]
        input_truncated = bool(listing["truncated"] or len(listing["files"]) > len(paths))
        indexed_bytes = 0
        for relative in paths:
            try:
                target = self._resolve(relative)
                text = self._read_text(target)
            except ToolError:
                continue
            text_bytes = len(text.encode("utf-8"))
            if indexed_bytes + text_bytes > MAX_CONTEXT_INDEX_BYTES:
                input_truncated = True
                break
            indexed_bytes += text_bytes
            symbols: list[dict[str, Any]] = []
            if target.suffix == ".py":
                inspected = self._inspect_cached(target, relative)
                if inspected["error"]:
                    parse_errors.append({"path": relative, "error": inspected["error"]})
                else:
                    symbols = inspected["symbols"]
            documents.append({"path": relative, "text": text, "symbols": symbols})
        matches = rank_repository_context(query, documents, limit=selected_limit)
        return {
            "query": query,
            "terms": list(terms),
            "matches": matches,
            "indexed_files": len(documents),
            "indexed_bytes": indexed_bytes,
            "parse_errors": parse_errors[:20],
            "truncated": input_truncated or len(matches) >= selected_limit,
        }

    def _backup(self, path: Path) -> None:
        relative = path.relative_to(self.root).as_posix()
        backup = self.backup_dir / relative
        if backup.exists() or relative in self._originally_missing:
            return
        if path.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, backup)
        else:
            self._originally_missing.add(relative)
            manifest = self.run_dir / "originally_missing.json"
            manifest.write_text(
                json.dumps(sorted(self._originally_missing), indent=2), encoding="utf-8"
            )

    def _ensure_write_budget(self, relative: str) -> None:
        projected = self.changed_files | {relative}
        if len(projected) > self.config.max_changed_files:
            raise ToolError(f"Changed-file budget exceeded ({self.config.max_changed_files}).")

    def edit_file(self, path: str, old_text: str, new_text: str) -> dict[str, Any]:
        target = self._resolve(path)
        current = self._read_text(target)
        count = current.count(old_text)
        if not old_text or count != 1:
            raise ToolError(f"old_text must match exactly once; found {count} matches.")
        updated = current.replace(old_text, new_text, 1)
        return self._stage_write(target, current, updated)

    def write_file(self, path: str, content: str) -> dict[str, Any]:
        target = self._resolve(path, allow_missing=True)
        if target.exists():
            raise ToolError("write_file only creates new files; use edit_file for existing files.")
        return self._stage_write(target, "", content)

    def _stage_write(self, target: Path, before: str, after: str) -> dict[str, Any]:
        encoded = after.encode("utf-8")
        if len(encoded) > self.config.max_file_bytes:
            raise ToolError(f"Result exceeds {self.config.max_file_bytes} byte limit.")
        relative = target.relative_to(self.root).as_posix()
        self._ensure_write_budget(relative)
        patch = "".join(
            difflib.unified_diff(
                before.splitlines(keepends=True),
                after.splitlines(keepends=True),
                fromfile=f"a/{relative}",
                tofile=f"b/{relative}",
            )
        )
        if not self.config.apply_changes:
            self._previews.append(patch)
            return {"path": relative, "applied": False, "preview": patch[:12_000]}
        self._backup(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(after, encoding="utf-8")
        self.changed_files.add(relative)
        return {"path": relative, "applied": True, "preview": patch[:12_000]}

    def _validate_command(self, command: str) -> list[str]:
        try:
            argv = shlex.split(command)
        except ValueError as exc:
            raise ToolError(f"Invalid command: {exc}") from exc
        if not argv:
            raise ToolError("Command cannot be empty.")
        if not any(
            tuple(argv[: len(prefix)]) == prefix for prefix in self.config.allowed_check_prefixes
        ):
            allowed = [" ".join(prefix) for prefix in self.config.allowed_check_prefixes]
            raise ToolError(f"Command is not allowlisted. Allowed prefixes: {allowed}")
        return argv

    def run_check(self, command: str) -> dict[str, Any]:
        if not self.config.allow_checks:
            raise ToolError("Check execution is disabled; start the agent with --allow-checks.")
        argv = self._validate_command(command)
        if argv[0] in {"python", "python3"}:
            executed_argv = [sys.executable, *argv[1:]]
        elif argv[0] == "pytest":
            executed_argv = [sys.executable, "-m", "pytest", *argv[1:]]
        else:
            executed_argv = argv
        safe_environment = {
            key: os.environ[key]
            for key in ("PATH", "LANG", "LC_ALL", "TMPDIR", "SYSTEMROOT")
            if key in os.environ
        }
        safe_environment["PYTHONDONTWRITEBYTECODE"] = "1"
        try:
            completed = subprocess.run(
                executed_argv,
                cwd=self.root,
                text=True,
                capture_output=True,
                timeout=self.config.command_timeout_seconds,
                env=safe_environment,
                check=False,
            )
            result = {
                "command": command,
                "executable": executed_argv[0],
                "exit_code": completed.returncode,
                "stdout": completed.stdout[-6000:],
                "stderr": completed.stderr[-6000:],
                "timed_out": False,
            }
        except subprocess.TimeoutExpired as exc:
            result = {
                "command": command,
                "executable": executed_argv[0],
                "exit_code": None,
                "stdout": (exc.stdout or "")[-6000:] if isinstance(exc.stdout, str) else "",
                "stderr": (exc.stderr or "")[-6000:] if isinstance(exc.stderr, str) else "",
                "timed_out": True,
            }
        self.checks.append(result)
        return result

    def diff(self) -> dict[str, Any]:
        if not self.config.apply_changes:
            value = "\n".join(self._previews)
            return {"diff": value[:40_000], "truncated": len(value) > 40_000}
        patches: list[str] = []
        for relative in sorted(self.changed_files):
            current_path = self.root / relative
            backup_path = self.backup_dir / relative
            before = backup_path.read_text(encoding="utf-8") if backup_path.exists() else ""
            after = current_path.read_text(encoding="utf-8") if current_path.exists() else ""
            patches.append(
                "".join(
                    difflib.unified_diff(
                        before.splitlines(keepends=True),
                        after.splitlines(keepends=True),
                        fromfile=f"a/{relative}",
                        tofile=f"b/{relative}",
                    )
                )
            )
        value = "\n".join(patches)
        return {"diff": value[:40_000], "truncated": len(value) > 40_000}

    def restore(self) -> list[str]:
        restored: list[str] = []
        for relative in sorted(self.changed_files):
            target = self.root / relative
            backup = self.backup_dir / relative
            if backup.is_symlink():
                raise ToolError(f"Backup is a symbolic link: {relative}")
            if backup.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup, target)
            elif relative in self._originally_missing and target.exists():
                target.unlink()
            restored.append(relative)
        return restored


def restore_run(root: Path, run_id: str) -> list[str]:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", run_id):
        raise ToolError("Invalid run id.")
    root = root.resolve()
    try:
        run_dir = safe_runs_dir(root) / run_id
    except ValueError as exc:
        raise ToolError(str(exc)) from exc
    result_path = run_dir / "result.json"
    if run_dir.is_symlink() or result_path.is_symlink():
        raise ToolError("Run storage contains a symbolic link.")
    if not result_path.is_file():
        raise ToolError(f"Run result not found: {run_id}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    changed = result.get("changed_files", [])
    if not isinstance(changed, list) or not all(isinstance(item, str) for item in changed):
        raise ToolError("Run result contains an invalid changed_files list.")
    config = AgentConfig(root=root, model="restore", apply_changes=True)
    tools = RepositoryTools(config, run_dir)
    tools.changed_files = set(changed)
    missing_path = run_dir / "originally_missing.json"
    if missing_path.exists():
        tools._originally_missing = set(json.loads(missing_path.read_text(encoding="utf-8")))
    for relative in tools.changed_files:
        tools._resolve(relative, allow_missing=True)
    return tools.restore()
