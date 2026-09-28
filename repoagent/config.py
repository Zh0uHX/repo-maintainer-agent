from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

TASK_MODES = ("edit", "localize")

DEFAULT_CHECK_PREFIXES = (
    ("python", "-m", "unittest"),
    ("python", "-m", "pytest"),
    ("python3", "-m", "unittest"),
    ("python3", "-m", "pytest"),
    ("pytest",),
    ("ruff", "check"),
    ("mypy",),
    ("npm", "test"),
    ("npm", "run", "test"),
    ("npm", "run", "lint"),
    ("pnpm", "test"),
    ("pnpm", "run", "lint"),
    ("cargo", "test"),
    ("cargo", "check"),
    ("go", "test"),
)


@dataclass(slots=True)
class AgentConfig:
    root: Path
    model: str
    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    apply_changes: bool = False
    allow_checks: bool = False
    enable_ast_tools: bool = True
    enable_context_retrieval: bool = True
    task_mode: str = "edit"
    ast_guidance: bool = False
    max_steps: int = 18
    max_changed_files: int = 12
    max_file_bytes: int = 512_000
    command_timeout_seconds: int = 120
    allowed_check_prefixes: tuple[tuple[str, ...], ...] = field(
        default_factory=lambda: DEFAULT_CHECK_PREFIXES
    )

    def __post_init__(self) -> None:
        if self.task_mode not in TASK_MODES:
            raise ValueError(f"task_mode must be one of {TASK_MODES}, got {self.task_mode!r}.")

    @classmethod
    def from_env(
        cls,
        root: str | Path,
        *,
        model: str | None = None,
        apply_changes: bool = False,
        allow_checks: bool = False,
        enable_ast_tools: bool = True,
        enable_context_retrieval: bool = True,
        base_url: str | None = None,
        api_key: str | None = None,
        max_steps: int = 18,
        task_mode: str = "edit",
        ast_guidance: bool = False,
    ) -> AgentConfig:
        selected_model = model or os.getenv("REPO_AGENT_MODEL")
        if not selected_model:
            raise ValueError("Set REPO_AGENT_MODEL or pass --model.")
        return cls(
            root=Path(root).expanduser().resolve(),
            model=selected_model,
            api_key=api_key if api_key is not None else os.getenv("REPO_AGENT_API_KEY"),
            base_url=base_url or os.getenv("REPO_AGENT_BASE_URL", "https://api.openai.com/v1"),
            apply_changes=apply_changes,
            allow_checks=allow_checks,
            enable_ast_tools=enable_ast_tools,
            enable_context_retrieval=enable_context_retrieval,
            max_steps=max_steps,
            task_mode=task_mode,
            ast_guidance=ast_guidance,
        )
