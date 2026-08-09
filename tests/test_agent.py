import json
import tempfile
import unittest
from pathlib import Path

from repoagent.agent import RepositoryAgent
from repoagent.config import AgentConfig
from repoagent.llm import ScriptedClient


class AgentTests(unittest.TestCase):
    def test_end_to_end_edit_and_trace(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
            responses = [
                {
                    "goal": "Update the value",
                    "steps": ["Inspect app.py", "Edit value", "Inspect diff"],
                    "risks": ["Wrong occurrence"],
                    "checks": [],
                },
                {
                    "thought_summary": "Inspect the target before editing.",
                    "action": {"name": "read_file", "args": {"path": "app.py"}},
                },
                {
                    "thought_summary": "Apply the exact requested replacement.",
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
                    "thought_summary": "Review the produced patch.",
                    "action": {"name": "diff", "args": {}},
                },
                {
                    "thought_summary": "The requested change is complete.",
                    "action": {
                        "name": "finish",
                        "args": {"status": "completed", "summary": "Updated VALUE to 2."},
                    },
                },
            ]
            config = AgentConfig(root=root, model="scripted", apply_changes=True, max_steps=6)
            result = RepositoryAgent(config, ScriptedClient(responses)).run("Set VALUE to 2")

            self.assertEqual(result.status, "completed")
            self.assertEqual(result.changed_files, ["app.py"])
            self.assertEqual((root / "app.py").read_text(), "VALUE = 2\n")
            self.assertIn("+VALUE = 2", result.diff)
            trace = [json.loads(line) for line in Path(result.trace_path).read_text().splitlines()]
            self.assertTrue(any(item["event"] == "tool_observation" for item in trace))

    def test_stops_after_repeated_invalid_actions(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            responses = [
                {"goal": "Task", "steps": ["Try"], "risks": [], "checks": []},
                *[
                    {
                        "thought_summary": "Try an unavailable tool.",
                        "action": {"name": "shell", "args": {"command": "ls"}},
                    }
                    for _ in range(4)
                ],
            ]
            config = AgentConfig(root=root, model="scripted", max_steps=10)
            result = RepositoryAgent(config, ScriptedClient(responses)).run("Do something")
            self.assertEqual(result.status, "failed")
            self.assertIn("four consecutive", result.summary)

    def test_cannot_report_completed_after_failed_final_check(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            responses = [
                {"goal": "Validate", "steps": ["Run tests"], "risks": [], "checks": ["tests"]},
                {
                    "thought_summary": "Run the test suite.",
                    "action": {
                        "name": "run_check",
                        "args": {"command": "python3 -m unittest discover -s missing_tests"},
                    },
                },
                {
                    "thought_summary": "Finish.",
                    "action": {
                        "name": "finish",
                        "args": {"status": "completed", "summary": "Done."},
                    },
                },
            ]
            config = AgentConfig(root=root, model="scripted", allow_checks=True, max_steps=3)
            result = RepositoryAgent(config, ScriptedClient(responses)).run("Validate")
            self.assertEqual(result.status, "failed")
            self.assertIn("final validation", result.summary)


if __name__ == "__main__":
    unittest.main()
