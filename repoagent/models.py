from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Plan:
    goal: str
    steps: list[str]
    risks: list[str] = field(default_factory=list)
    checks: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Plan:
        goal = value.get("goal")
        steps = value.get("steps")
        if (
            not isinstance(goal, str)
            or not isinstance(steps, list)
            or not all(isinstance(item, str) for item in steps)
        ):
            raise ValueError("Plan must contain a string goal and a list of string steps.")
        return cls(
            goal=goal,
            steps=steps,
            risks=[str(item) for item in value.get("risks", [])],
            checks=[str(item) for item in value.get("checks", [])],
        )


@dataclass(slots=True)
class AgentResult:
    run_id: str
    status: str
    summary: str
    plan: Plan
    changed_files: list[str]
    checks: list[dict[str, Any]]
    trace_path: str
    diff: str = ""
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["plan"] = asdict(self.plan)
        return value
