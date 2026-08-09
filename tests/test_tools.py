import json
import sys
import tempfile
import unittest
from pathlib import Path

from repoagent.config import AgentConfig
from repoagent.tools import RepositoryTools, ToolError, restore_run


class RepositoryToolsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "src").mkdir()
        (self.root / "src" / "maths.py").write_text(
            "def add(a, b):\n    return a - b\n", encoding="utf-8"
        )
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_smoke.py").write_text(
            "import unittest\n\n"
            "class SmokeTest(unittest.TestCase):\n"
            "    def test_true(self):\n"
            "        self.assertTrue(True)\n",
            encoding="utf-8",
        )
        (self.root / ".env").write_text("SECRET=value\n", encoding="utf-8")
        (self.root / ".env.production").write_text("SECRET=value\n", encoding="utf-8")
        self.run_dir = self.root / ".repoagent" / "runs" / "test"
        config = AgentConfig(root=self.root, model="test", apply_changes=True, allow_checks=True)
        self.tools = RepositoryTools(config, self.run_dir)

    def tearDown(self):
        self.temporary.cleanup()

    def test_list_excludes_secrets_and_internal_state(self):
        files = self.tools.list_files()["files"]
        self.assertIn("src/maths.py", files)
        self.assertNotIn(".env", files)
        self.assertNotIn(".env.production", files)
        self.assertFalse(any(path.startswith(".repoagent") for path in files))

    def test_read_with_line_numbers(self):
        result = self.tools.read_file("src/maths.py")
        self.assertIn("1: def add", result["content"])

    def test_search(self):
        result = self.tools.search("return a - b", glob="*.py")
        self.assertEqual(result["matches"][0]["line"], 2)

    def test_rejects_escape_and_secret(self):
        with self.assertRaises(ToolError):
            self.tools.read_file("../outside.txt")
        with self.assertRaises(ToolError):
            self.tools.read_file(".env")
        with self.assertRaises(ToolError):
            self.tools.read_file(".env.production")

    def test_edit_diff_and_restore(self):
        result = self.tools.edit_file("src/maths.py", "return a - b", "return a + b")
        self.assertTrue(result["applied"])
        self.assertIn("return a + b", (self.root / "src" / "maths.py").read_text())
        self.assertIn("+    return a + b", self.tools.diff()["diff"])
        self.tools.restore()
        self.assertIn("return a - b", (self.root / "src" / "maths.py").read_text())

    def test_new_file_restore_removes_it(self):
        self.tools.write_file("src/new.py", "VALUE = 1\n")
        self.assertTrue((self.root / "src" / "new.py").exists())
        self.tools.restore()
        self.assertFalse((self.root / "src" / "new.py").exists())

    def test_restore_completed_run_from_disk(self):
        self.tools.edit_file("src/maths.py", "return a - b", "return a + b")
        result = {"changed_files": ["src/maths.py"]}
        (self.run_dir / "result.json").write_text(json.dumps(result), encoding="utf-8")
        restored = restore_run(self.root, "test")
        self.assertEqual(restored, ["src/maths.py"])
        self.assertIn("return a - b", (self.root / "src" / "maths.py").read_text())

    def test_edit_requires_unique_match(self):
        with self.assertRaises(ToolError):
            self.tools.edit_file("src/maths.py", "a", "x")

    def test_preview_does_not_write(self):
        config = AgentConfig(root=self.root, model="test", apply_changes=False)
        tools = RepositoryTools(config, self.root / ".repoagent" / "runs" / "preview")
        result = tools.edit_file("src/maths.py", "return a - b", "return a + b")
        self.assertFalse(result["applied"])
        self.assertIn("return a - b", (self.root / "src" / "maths.py").read_text())
        self.assertIn("+    return a + b", tools.diff()["diff"])

    def test_command_allowlist(self):
        with self.assertRaises(ToolError):
            self.tools.run_check("curl https://example.com")
        result = self.tools.run_check("python3 -m unittest discover -s tests")
        self.assertEqual(result["exit_code"], 0)

    def test_python_alias_uses_current_interpreter(self):
        result = self.tools.run_check("python -m unittest discover -s tests")
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["executable"], sys.executable)

    def test_pytest_alias_uses_current_interpreter(self):
        result = self.tools.run_check("pytest -q")
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["executable"], sys.executable)


if __name__ == "__main__":
    unittest.main()
