import functools
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from repoagent import realrepo
from repoagent.config import AgentConfig
from repoagent.evals import evaluate_case, export_predictions
from repoagent.llm import ScriptedClient
from repoagent.metrics import aggregate_results

SOURCE = """\
import os


class Session:
    def get(self, url):
        return self.request("GET", url)

    def request(self, method, url):
        if not url:
            raise ValueError("url")
        return method, url


def helper():
    return 1
"""

PATCH = """\
diff --git a/pkg/sessions.py b/pkg/sessions.py
--- a/pkg/sessions.py
+++ b/pkg/sessions.py
@@ -8,5 +8,5 @@ def get(self, url):
     def request(self, method, url):
-        if not url:
+        if url is None:
             raise ValueError("url")
         return method, url

@@ -14,2 +14,3 @@ def request(self, method, url):
 def helper():
+    # documented
     return 1
"""


def _git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class PatchParsingTests(unittest.TestCase):
    def test_changed_lines_and_enclosing_symbols(self):
        lines = realrepo.changed_old_lines(PATCH)
        self.assertEqual(lines, {"pkg/sessions.py": [9, 14]})
        self.assertEqual(
            realrepo.enclosing_symbols(SOURCE, lines["pkg/sessions.py"]),
            ["Session.request", "helper"],
        )

    def test_score_localization_ranks_files_and_symbols(self):
        gold = {
            "files": ["pkg/sessions.py"],
            "functions": [
                {"path": "pkg/sessions.py", "symbol": "Session.request"},
                {"path": "pkg/sessions.py", "symbol": "helper"},
            ],
        }
        predicted = [
            {"path": "pkg/api.py", "symbol": "get"},
            {"path": "pkg/sessions.py", "symbol": "request"},
            {"path": "pkg/api.py", "symbol": "post"},
        ]
        scores = realrepo.score_localization(predicted, gold)
        self.assertFalse(scores["file_acc@1"])
        self.assertTrue(scores["file_acc@3"])
        self.assertEqual(scores["function_recall@1"], 0.0)
        self.assertEqual(scores["function_recall@3"], 0.5)
        self.assertEqual(scores["predicted_files"], ["pkg/api.py", "pkg/sessions.py"])


class RealRepositoryHarnessTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        base = Path(self.temporary.name)
        work = base / "work"
        (work / "pkg").mkdir(parents=True)
        (work / "pkg" / "sessions.py").write_text(SOURCE, encoding="utf-8")
        _git("init", "-q", cwd=work)
        _git("add", ".", cwd=work)
        _git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "base", cwd=work)
        self.commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=work, check=True, capture_output=True, text=True
        ).stdout.strip()
        self.cache = base / "cache"
        self.cache.mkdir()
        _git("clone", "-q", "--bare", str(work), str(self.cache / "acme__widgets.git"), cwd=base)

    def tearDown(self):
        self.temporary.cleanup()

    def test_materialize_and_gold_locations_use_cached_clone(self):
        with tempfile.TemporaryDirectory() as target:
            realrepo.materialize("acme/widgets", self.commit, Path(target), self.cache)
            self.assertEqual((Path(target) / "pkg" / "sessions.py").read_text(), SOURCE)
            self.assertFalse((Path(target) / ".git").exists())
        gold = realrepo.gold_locations("acme/widgets", self.commit, PATCH, self.cache)
        self.assertEqual(gold["files"], ["pkg/sessions.py"])
        self.assertEqual(
            [item["symbol"] for item in gold["functions"]], ["Session.request", "helper"]
        )
        self.assertEqual(realrepo.python_file_count("acme/widgets", self.commit, self.cache), 1)

    def test_rejects_unsafe_repository_and_commit_values(self):
        with self.assertRaises(ValueError):
            realrepo.cached_clone("../etc", self.cache)
        with self.assertRaises(ValueError):
            realrepo.materialize("acme/widgets", "--output=/tmp/x", Path("."), self.cache)

    def test_localize_case_is_scored_and_keeps_only_run_records(self):
        case = {
            "name": "acme__widgets-1",
            "instance_id": "acme__widgets-1",
            "family": "small",
            "mode": "localize",
            "repo": "acme/widgets",
            "base_commit": self.commit,
            "task": "Empty URLs are rejected by Session.request.",
            "gold": realrepo.gold_locations("acme/widgets", self.commit, PATCH, self.cache),
        }
        responses = [
            {"goal": "Locate", "steps": ["Inspect"], "risks": [], "checks": []},
            {
                "thought_summary": "Find request.",
                "action": {"name": "symbol_search", "args": {"name": "request"}},
            },
            {
                "thought_summary": "Report.",
                "action": {
                    "name": "finish",
                    "args": {
                        "status": "completed",
                        "summary": "The URL guard is in Session.request.",
                        "locations": [{"path": "pkg/sessions.py", "symbol": "Session.request"}],
                    },
                },
            },
        ]
        config = AgentConfig(root=Path("."), model="scripted", max_steps=4)
        materialize = functools.partial(realrepo.materialize, cache_dir=self.cache)
        with (
            tempfile.TemporaryDirectory() as artifacts,
            mock.patch("repoagent.evals.materialize", materialize),
        ):
            result = evaluate_case(case, config, ScriptedClient(responses), Path(artifacts))
            preserved = Path(artifacts) / "acme__widgets-1"
            self.assertTrue(list(preserved.glob("runs/*/trace.jsonl")))
            self.assertFalse((preserved / "pkg").exists())

        self.assertTrue(result["passed"])
        self.assertTrue(result["localization"]["file_acc@1"])
        self.assertEqual(result["localization"]["function_recall@1"], 0.5)
        self.assertNotIn("model_patch", result)
        summary = aggregate_results([result])["localization"]
        self.assertEqual(summary["cases"], 1)
        self.assertEqual(summary["file_acc@1"], 1.0)
        self.assertEqual(export_predictions({"results": [result]}, "m"), [])


if __name__ == "__main__":
    unittest.main()
