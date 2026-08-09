import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from fastapi.testclient import TestClient

    from repoagent.api import app
except (ImportError, RuntimeError):  # Optional API dependencies are not installed.
    TestClient = None
    app = None


@unittest.skipIf(TestClient is None, "API test dependencies are not installed")
class ApiTests(unittest.TestCase):
    def test_dashboard_history_and_write_guard(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run = root / ".repoagent" / "runs" / "20260101T000000Z-api"
            run.mkdir(parents=True)
            result = {
                "status": "completed",
                "summary": "Demo run",
                "changed_files": [],
                "metrics": {"tool_calls": 2, "tool_errors": 0},
            }
            (run / "result.json").write_text(json.dumps(result), encoding="utf-8")
            (run / "trace.jsonl").write_text("", encoding="utf-8")

            environment = {"REPO_AGENT_ALLOWED_ROOT": str(root)}
            with patch.dict(os.environ, environment, clear=True):
                client = TestClient(app)
                dashboard = client.get("/")
                self.assertEqual(dashboard.status_code, 200)
                self.assertIn("RepoAgent Observatory", dashboard.text)
                history = client.get("/history")
                self.assertEqual(history.json()["total_runs"], 1)
                detail = client.get("/runs/20260101T000000Z-api")
                self.assertEqual(detail.json()["result"]["summary"], "Demo run")
                denied = client.post(
                    "/runs",
                    json={"task": "Change a file", "root": str(root), "apply_changes": True},
                )
                self.assertEqual(denied.status_code, 403)


if __name__ == "__main__":
    unittest.main()
