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

    def test_localize_mode_requires_locations_and_blocks_edits(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "app.py").write_text("def run():\n    return 1\n", encoding="utf-8")
            responses = [
                {"goal": "Locate", "steps": ["Search"], "risks": [], "checks": []},
                {
                    "thought_summary": "Try to edit.",
                    "action": {
                        "name": "edit_file",
                        "args": {"path": "app.py", "old_text": "1", "new_text": "2"},
                    },
                },
                {
                    "thought_summary": "Finish without locations.",
                    "action": {"name": "finish", "args": {"status": "completed", "summary": "x"}},
                },
                {
                    "thought_summary": "Report the location.",
                    "action": {
                        "name": "finish",
                        "args": {
                            "status": "completed",
                            "summary": "run() returns the value.",
                            "locations": [{"path": "./app.py", "symbol": "run"}, "other.py"],
                        },
                    },
                },
            ]
            config = AgentConfig(root=root, model="scripted", task_mode="localize", max_steps=5)
            result = RepositoryAgent(config, ScriptedClient(responses)).run("Find the bug")

            self.assertEqual(result.status, "completed")
            self.assertEqual(
                result.locations,
                [{"path": "app.py", "symbol": "run"}, {"path": "other.py", "symbol": ""}],
            )
            self.assertEqual((root / "app.py").read_text(), "def run():\n    return 1\n")
            trace = [json.loads(line) for line in Path(result.trace_path).read_text().splitlines()]
            errors = [
                item["payload"]["error"]
                for item in trace
                if item["event"] == "tool_observation" and not item["payload"]["ok"]
            ]
            self.assertIn("Unknown tool: edit_file", errors[0])
            self.assertIn("locations", errors[1])

    def test_old_observations_are_compacted_and_budget_is_reported(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
            reads = [
                {
                    "thought_summary": "Read again.",
                    "action": {"name": "read_file", "args": {"path": "app.py"}},
                }
                for _ in range(8)
            ]
            client = RecordingClient(
                [{"goal": "Read", "steps": ["Read"], "risks": [], "checks": []}, *reads]
            )
            config = AgentConfig(root=root, model="scripted", max_steps=8)
            result = RepositoryAgent(config, client).run("Read app.py")

            self.assertEqual(result.status, "failed")
            final = client.calls[-1]
            observations = [m["content"] for m in final if m["content"].startswith("Tool obs")]
            self.assertEqual(len(observations), 7)
            elided = [text for text in observations if "elided" in text]
            self.assertEqual(len(elided), 1)
            self.assertNotIn("VALUE = 1", elided[0])
            self.assertIn("Steps used: 7/8", observations[-1])
            self.assertIn("Only 1 step(s) remain", observations[-1])


class RecordingClient(ScriptedClient):
    def __init__(self, responses):
        super().__init__(responses)
        self.calls = []

    def complete(self, messages):
        self.calls.append([dict(message) for message in messages])
        return super().complete(messages)


if __name__ == "__main__":
    unittest.main()
