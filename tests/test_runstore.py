import json
import tempfile
import unittest
from pathlib import Path

from repoagent.runstore import history_report, list_runs, load_run, safe_runs_dir


class RunStoreTests(unittest.TestCase):
    def test_lists_loads_and_aggregates_runs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run = root / ".repoagent" / "runs" / "20260101T000000Z-test"
            run.mkdir(parents=True)
            result = {
                "status": "completed",
                "summary": "Fixed bug",
                "changed_files": ["app.py"],
                "metrics": {
                    "changed_files": 1,
                    "tool_calls": 4,
                    "tool_errors": 1,
                    "total_tokens": 50,
                },
            }
            (run / "result.json").write_text(json.dumps(result), encoding="utf-8")
            (run / "trace.jsonl").write_text(
                json.dumps({"event": "finish", "payload": {"step": 3}}) + "\n", encoding="utf-8"
            )

            self.assertEqual(list_runs(root)[0]["status"], "completed")
            self.assertEqual(len(load_run(root, run.name)["trace"]), 1)
            report = history_report(root)
            self.assertEqual(report["completion_rate"], 1.0)
            self.assertEqual(report["tool_calls"], 4)

    def test_rejects_invalid_run_id(self):
        with tempfile.TemporaryDirectory() as temporary, self.assertRaises(ValueError):
            load_run(Path(temporary), "../escape")

    def test_rejects_symlinked_storage(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outside = root / "outside"
            outside.mkdir()
            (root / ".repoagent").symlink_to(outside, target_is_directory=True)
            with self.assertRaises(ValueError):
                safe_runs_dir(root, create=True)


if __name__ == "__main__":
    unittest.main()
