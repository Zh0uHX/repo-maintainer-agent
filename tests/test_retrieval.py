import tempfile
import unittest
from pathlib import Path

from repoagent.config import AgentConfig
from repoagent.retrieval import query_terms, rank_repository_context
from repoagent.tools import RepositoryTools, ToolError


class RepositoryRetrievalTests(unittest.TestCase):
    def test_tokenizes_snake_case_and_camel_case(self):
        self.assertEqual(
            query_terms("Locate InvoiceCalculator.compute_total method"),
            ("locate", "invoice", "calculator", "compute", "total"),
        )

    def test_ranks_ast_symbol_and_returns_numbered_evidence(self):
        documents = [
            {
                "path": "billing/calculator.py",
                "text": (
                    "class InvoiceCalculator:\n"
                    "    def compute_total(self, items):\n"
                    "        return sum(item.price for item in items)\n"
                ),
                "symbols": [
                    {
                        "qualified_name": "InvoiceCalculator.compute_total",
                        "kind": "method",
                        "line": 2,
                        "end_line": 3,
                    }
                ],
            },
            {
                "path": "analytics/calculator.py",
                "text": "def compute_average(values):\n    return sum(values) / len(values)\n",
                "symbols": [
                    {
                        "qualified_name": "compute_average",
                        "kind": "function",
                        "line": 1,
                        "end_line": 2,
                    }
                ],
            },
        ]

        matches = rank_repository_context("invoice total calculation", documents, limit=2)

        self.assertEqual(matches[0]["path"], "billing/calculator.py")
        self.assertEqual(matches[0]["symbol"], "InvoiceCalculator.compute_total")
        self.assertIn("2:     def compute_total", matches[0]["content"])
        self.assertIn("invoice", matches[0]["matched_terms"])

    def test_tool_respects_repository_policy_and_can_be_disabled(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            (root / "service.py").write_text(
                "def load_customer_profile(customer_id):\n    return customer_id\n",
                encoding="utf-8",
            )
            (root / ".env").write_text("SECRET=do-not-index\n", encoding="utf-8")
            tools = RepositoryTools(
                AgentConfig(root=root, model="test"), root / ".repoagent" / "runs" / "retrieval"
            )

            result = tools.retrieve_context("customer profile")

            self.assertEqual(result["indexed_files"], 1)
            self.assertEqual(result["matches"][0]["path"], "service.py")
            self.assertNotIn("do-not-index", str(result))

            disabled = RepositoryTools(
                AgentConfig(root=root, model="test", enable_context_retrieval=False),
                root / ".repoagent" / "runs" / "disabled-retrieval",
            )
            with self.assertRaises(ToolError):
                disabled.execute("retrieve_context", {"query": "customer"})

    def test_tool_caps_repository_scan_and_validates_limit(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            for index in range(245):
                (root / f"module_{index:03}.py").write_text(
                    f"VALUE_{index} = 'needle'\n", encoding="utf-8"
                )
            tools = RepositoryTools(
                AgentConfig(root=root, model="test"), root / ".repoagent" / "runs" / "bounded"
            )

            result = tools.retrieve_context("needle", limit=2)

            self.assertEqual(result["indexed_files"], 240)
            self.assertTrue(result["truncated"])
            with self.assertRaises(ToolError):
                tools.retrieve_context("needle", limit="many")


if __name__ == "__main__":
    unittest.main()
