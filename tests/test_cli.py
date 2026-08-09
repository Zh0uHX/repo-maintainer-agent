import json
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch

from repoagent.cli import main
from repoagent.llm import ScriptedClient


class CliEvaluationTests(unittest.TestCase):
    def test_version_matches_package(self):
        output = StringIO()
        with self.assertRaises(SystemExit) as raised, redirect_stdout(output):
            main(["--version"])
        self.assertEqual(raised.exception.code, 0)
        self.assertIn("repoagent 0.4.0", output.getvalue())

    def test_eval_checkpoints_model_error_and_writes_artifact(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cases = root / "cases.jsonl"
            output = root / "report.json"
            markdown = root / "report.md"
            artifacts = root / "artifacts"
            cases.write_text(
                json.dumps(
                    {
                        "name": "error-case",
                        "task": "Change VALUE.",
                        "files": {"app.py": "VALUE = 1\n"},
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            with patch("repoagent.cli.OpenAICompatibleClient", return_value=ScriptedClient([])):
                exit_code = main(
                    [
                        "eval",
                        str(cases),
                        "--model",
                        "scripted",
                        "--output",
                        str(output),
                        "--markdown",
                        str(markdown),
                        "--artifacts",
                        str(artifacts),
                    ]
                )

            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 2)
            self.assertEqual(report["results"][0]["status"], "error")
            self.assertIn("Scripted model has no response left", markdown.read_text())
            self.assertTrue((artifacts / "error-case" / "evaluation-error.json").is_file())

    def test_resume_skips_completed_case(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            cases = root / "cases.jsonl"
            output = root / "report.json"
            cases.write_text(
                json.dumps({"name": "done", "task": "No-op.", "files": {}}) + "\n",
                encoding="utf-8",
            )
            output.write_text(
                json.dumps(
                    {
                        "model": "scripted",
                        "ast_enabled": True,
                        "context_retrieval_enabled": True,
                        "results": [
                            {
                                "name": "done",
                                "family": "test",
                                "passed": True,
                                "status": "completed",
                                "metrics": {},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            with patch("repoagent.cli.OpenAICompatibleClient", return_value=ScriptedClient([])):
                exit_code = main(
                    [
                        "eval",
                        str(cases),
                        "--model",
                        "scripted",
                        "--output",
                        str(output),
                        "--resume",
                    ]
                )

            report = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(exit_code, 0)
            self.assertEqual(report["total"], 1)
            self.assertEqual(report["passed"], 1)


if __name__ == "__main__":
    unittest.main()
