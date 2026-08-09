import tempfile
import unittest
from pathlib import Path

from repoagent.demo import run_demo


class DemoTests(unittest.TestCase):
    def test_demo_reproduces_fixes_and_verifies_bug(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "demo"
            result = run_demo(destination)
            self.assertEqual(result.status, "completed")
            self.assertEqual(result.changed_files, ["calculator.py"])
            self.assertEqual(result.metrics["checks_passed"], 1)
            self.assertEqual(result.metrics["checks_failed"], 1)
            self.assertIn("raise ValueError", (destination / "calculator.py").read_text())
            self.assertIn("+            raise ValueError", result.diff)


if __name__ == "__main__":
    unittest.main()
