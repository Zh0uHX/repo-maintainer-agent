import tempfile
import unittest
from pathlib import Path

from repoagent.config import AgentConfig
from repoagent.tools import RepositoryTools, ToolError

SOURCE = '''import json
from pathlib import Path

class Greeter:
    """Create greetings."""

    def greet(self, name: str) -> str:
        return f"Hello, {name}"

async def fetch_value(key: str) -> int:
    return 1
'''


class PythonIndexTests(unittest.TestCase):
    def test_inspect_and_symbol_search(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "service.py").write_text(SOURCE, encoding="utf-8")
            config = AgentConfig(root=root, model="test")
            tools = RepositoryTools(config, root / ".repoagent" / "runs" / "index")

            result = tools.inspect_python("service.py")
            names = {item["qualified_name"] for item in result["symbols"]}
            self.assertEqual(names, {"Greeter", "Greeter.greet", "fetch_value"})
            self.assertEqual(result["symbols"][0]["docstring"], "Create greetings.")
            self.assertEqual(len(result["imports"]), 2)

            search = tools.symbol_search("greet")
            self.assertEqual(
                {item["qualified_name"] for item in search["matches"]},
                {"Greeter", "Greeter.greet"},
            )

    def test_reports_syntax_error(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "broken.py").write_text("def broken(:\n", encoding="utf-8")
            tools = RepositoryTools(
                AgentConfig(root=root, model="test"), root / ".repoagent" / "runs" / "index"
            )
            self.assertIsNotNone(tools.inspect_python("broken.py")["error"])

    def test_ast_tools_can_be_disabled_for_ablation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "service.py").write_text(SOURCE, encoding="utf-8")
            tools = RepositoryTools(
                AgentConfig(root=root, model="test", enable_ast_tools=False),
                root / ".repoagent" / "runs" / "index",
            )
            with self.assertRaises(ToolError):
                tools.execute("symbol_search", {"name": "greet"})


if __name__ == "__main__":
    unittest.main()
