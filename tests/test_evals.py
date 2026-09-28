import json
import tempfile
import unittest
from pathlib import Path

from repoagent.config import AgentConfig
from repoagent.evals import evaluate_case, merge_benchmark_reports
from repoagent.llm import ScriptedClient


class EvaluationTests(unittest.TestCase):
    def test_model_error_is_reported_and_preserves_case_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifacts = root / "artifacts"
            config = AgentConfig(root=root, model="scripted")
            case = {
                "name": "interrupted-case",
                "task": "Change VALUE.",
                "files": {"app.py": "VALUE = 1\n"},
            }

            result = evaluate_case(case, config, ScriptedClient([]), artifacts)

            self.assertFalse(result["passed"])
            self.assertEqual(result["status"], "error")
            self.assertIn("Scripted model has no response left", result["error"])
            self.assertEqual(result["metrics"]["model_errors"], 1)
            self.assertEqual(result["metrics"]["request_attempts"], 1)
            destination = artifacts / "interrupted-case"
            self.assertEqual((destination / "app.py").read_text(), "VALUE = 1\n")
            self.assertTrue((destination / "evaluation-error.json").is_file())
            self.assertEqual(len(list(destination.glob(".repoagent/runs/*/trace.jsonl"))), 1)

    def test_merge_replaces_retried_case_and_recalculates_metrics(self):
        base = {
            "model": "m",
            "ast_enabled": True,
            "results": [
                {"name": "a", "family": "f", "passed": True, "metrics": {}},
                {"name": "b", "family": "f", "passed": False, "metrics": {}},
            ],
        }
        update = {
            "model": "m",
            "ast_enabled": True,
            "results": [{"name": "b", "family": "f", "passed": True, "metrics": {}}],
        }
        merged = merge_benchmark_reports(base, update)
        self.assertEqual(merged["passed"], 2)
        self.assertEqual(merged["pass_rate"], 1.0)

    def test_uses_independent_checks_and_change_scope(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = AgentConfig(root=root, model="scripted")
            client = ScriptedClient(
                [
                    {"goal": "Fix value", "steps": ["read", "edit"], "risks": [], "checks": []},
                    {
                        "thought_summary": "Inspect source.",
                        "action": {"name": "read_file", "args": {"path": "app.py"}},
                    },
                    {
                        "thought_summary": "Fix source.",
                        "action": {
                            "name": "edit_file",
                            "args": {
                                "path": "app.py",
                                "old_text": "VALUE = 1",
                                "new_text": "VALUE = 2",
                            },
                        },
                    },
                    {
                        "thought_summary": "Done.",
                        "action": {
                            "name": "finish",
                            "args": {"status": "completed", "summary": "Fixed."},
                        },
                    },
                ]
            )
            case = {
                "name": "value-fix",
                "task": "Set VALUE to 2.",
                "files": {
                    "app.py": "VALUE = 1\n",
                },
                "hidden_files": {
                    "hidden_tests/test_app.py": (
                        "import unittest\nfrom app import VALUE\n\n"
                        "class AppTest(unittest.TestCase):\n"
                        "    def test_value(self):\n        self.assertEqual(VALUE, 2)\n"
                    ),
                },
                "contains": {"app.py": ["VALUE = 2"]},
                "allowed_changed_files": ["app.py"],
                "check_commands": ["python -m unittest discover -s hidden_tests"],
                "mutations": [
                    {
                        "path": "app.py",
                        "content": "VALUE = 1\n",
                        "check_command": "python -m unittest discover -s hidden_tests",
                    }
                ],
            }
            result = evaluate_case(case, config, client)
            self.assertTrue(result["passed"])
            self.assertEqual(result["benchmark_checks"][0]["exit_code"], 0)
            self.assertTrue(all(item["passed"] for item in result["assertions"]))
            self.assertTrue(result["mutation_checks"][0]["killed"])

    def test_passing_case_preserves_full_trace_when_artifacts_requested(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            artifacts = root / "artifacts"
            config = AgentConfig(root=root, model="scripted")
            client = ScriptedClient(
                [
                    {"goal": "Fix value", "steps": ["read", "edit"], "risks": [], "checks": []},
                    {
                        "thought_summary": "Inspect source.",
                        "action": {"name": "read_file", "args": {"path": "app.py"}},
                    },
                    {
                        "thought_summary": "Fix source.",
                        "action": {
                            "name": "edit_file",
                            "args": {
                                "path": "app.py",
                                "old_text": "VALUE = 1",
                                "new_text": "VALUE = 2",
                            },
                        },
                    },
                    {
                        "thought_summary": "Done.",
                        "action": {
                            "name": "finish",
                            "args": {"status": "completed", "summary": "Fixed."},
                        },
                    },
                ]
            )
            case = {
                "name": "passing-case",
                "task": "Set VALUE to 2.",
                "files": {"app.py": "VALUE = 1\n"},
                "contains": {"app.py": ["VALUE = 2"]},
                "allowed_changed_files": ["app.py"],
            }

            result = evaluate_case(case, config, client, artifacts)

            self.assertTrue(result["passed"])
            destination = artifacts / "passing-case"
            traces = list(destination.glob(".repoagent/runs/*/trace.jsonl"))
            self.assertEqual(len(traces), 1)
            lines = [line for line in traces[0].read_text(encoding="utf-8").splitlines() if line.strip()]
            self.assertGreater(len(lines), 0)
            events = [json.loads(line)["event"] for line in lines]
            self.assertIn("run_started", events)
            self.assertIn("finish", events)
            self.assertEqual(result["metrics"]["completed"], True)


if __name__ == "__main__":
    unittest.main()
