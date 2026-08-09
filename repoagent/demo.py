from __future__ import annotations

from pathlib import Path

from .agent import RepositoryAgent
from .config import AgentConfig
from .llm import ScriptedClient
from .models import AgentResult

DEMO_RESPONSES = [
    {
        "goal": "Fix Calculator.divide so division by zero is rejected explicitly.",
        "steps": [
            "Inspect the implementation and symbols",
            "Read the regression test",
            "Run the test to reproduce the failure",
            "Apply a minimal fix",
            "Re-run tests and inspect the diff",
        ],
        "risks": ["Changing valid division behavior"],
        "checks": ["python3 -m unittest discover -s tests -v"],
    },
    {
        "thought_summary": "Inspect the target symbol and imports before editing.",
        "action": {"name": "inspect_python", "args": {"path": "calculator.py"}},
    },
    {
        "thought_summary": "Read the regression test to establish the required behavior.",
        "action": {"name": "read_file", "args": {"path": "tests/test_calculator.py"}},
    },
    {
        "thought_summary": "Reproduce the reported failure before changing code.",
        "action": {
            "name": "run_check",
            "args": {"command": "python3 -m unittest discover -s tests -v"},
        },
    },
    {
        "thought_summary": "Add the smallest guard that satisfies the regression test.",
        "action": {
            "name": "edit_file",
            "args": {
                "path": "calculator.py",
                "old_text": "    def divide(self, numerator, denominator):\n        return numerator / denominator\n",
                "new_text": (
                    "    def divide(self, numerator, denominator):\n"
                    "        if denominator == 0:\n"
                    '            raise ValueError("denominator must not be zero")\n'
                    "        return numerator / denominator\n"
                ),
            },
        },
    },
    {
        "thought_summary": "Verify the fix against the full demo test suite.",
        "action": {
            "name": "run_check",
            "args": {"command": "python3 -m unittest discover -s tests -v"},
        },
    },
    {
        "thought_summary": "Review the exact repository change before completion.",
        "action": {"name": "diff", "args": {}},
    },
    {
        "thought_summary": "The regression test passes and the diff is limited to the target method.",
        "action": {
            "name": "finish",
            "args": {
                "status": "completed",
                "summary": "Added explicit zero-denominator validation and verified both tests.",
            },
        },
    },
]


def run_demo(destination: Path) -> AgentResult:
    destination = destination.expanduser().resolve()
    if destination.exists() and any(destination.iterdir()):
        raise ValueError(f"Demo destination must be empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    tests = destination / "tests"
    tests.mkdir()
    (destination / "calculator.py").write_text(
        "class Calculator:\n"
        "    def divide(self, numerator, denominator):\n"
        "        return numerator / denominator\n",
        encoding="utf-8",
    )
    (tests / "test_calculator.py").write_text(
        "import unittest\n\n"
        "from calculator import Calculator\n\n\n"
        "class CalculatorTests(unittest.TestCase):\n"
        "    def test_valid_division(self):\n"
        "        self.assertEqual(Calculator().divide(8, 2), 4)\n\n"
        "    def test_zero_denominator_has_domain_error(self):\n"
        "        with self.assertRaisesRegex(ValueError, 'denominator'):\n"
        "            Calculator().divide(8, 0)\n\n\n"
        "if __name__ == '__main__':\n"
        "    unittest.main()\n",
        encoding="utf-8",
    )
    config = AgentConfig(
        root=destination,
        model="scripted-demo",
        apply_changes=True,
        allow_checks=True,
        max_steps=10,
    )
    return RepositoryAgent(config, ScriptedClient(DEMO_RESPONSES)).run(
        "Make Calculator.divide reject a zero denominator with a clear ValueError."
    )
