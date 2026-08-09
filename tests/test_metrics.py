import json
import tempfile
import unittest
from pathlib import Path

from repoagent.evals import render_markdown_report
from repoagent.metrics import aggregate_results, summarize_trace


class MetricsTests(unittest.TestCase):
    def test_summarizes_trace_and_usage(self):
        with tempfile.TemporaryDirectory() as temporary:
            trace = Path(temporary) / "trace.jsonl"
            records = [
                {
                    "event": "model_response",
                    "payload": {
                        "latency_ms": 25,
                        "model_metadata": {
                            "usage": {
                                "prompt_tokens": 10,
                                "completion_tokens": 4,
                                "total_tokens": 14,
                            }
                        },
                    },
                },
                {
                    "event": "tool_observation",
                    "payload": {"step": 1, "tool": "read_file", "ok": True},
                },
                {
                    "event": "tool_observation",
                    "payload": {"step": 2, "tool": "edit_file", "ok": False},
                },
                {"event": "finish", "payload": {"step": 3}},
            ]
            trace.write_text("\n".join(json.dumps(item) for item in records), encoding="utf-8")
            metrics = summarize_trace(
                trace,
                status="completed",
                changed_files=1,
                checks=[{"exit_code": 0, "timed_out": False}],
            )
            self.assertEqual(metrics["steps"], 3)
            self.assertEqual(metrics["tool_errors"], 1)
            self.assertEqual(metrics["total_tokens"], 14)
            self.assertEqual(metrics["checks_passed"], 1)

    def test_aggregates_benchmark_results(self):
        report = aggregate_results(
            [
                {
                    "passed": True,
                    "family": "bug-fix",
                    "metrics": {
                        "steps": 4,
                        "tool_calls": 3,
                        "total_tokens": 10,
                        "tool_counts": {"inspect_python": 1, "retrieve_context": 1},
                    },
                },
                {
                    "passed": False,
                    "family": "bug-fix",
                    "metrics": {"steps": 6, "tool_calls": 5, "total_tokens": 20},
                },
            ]
        )
        self.assertEqual(report["pass_rate"], 0.5)
        self.assertEqual(report["average_steps"], 5.0)
        self.assertEqual(report["total_tokens"], 30)
        self.assertEqual(report["ast_tool_calls"], 1)
        self.assertEqual(report["context_retrieval_calls"], 1)
        self.assertEqual(report["families"]["bug-fix"]["pass_rate"], 0.5)
        report["results"] = [
            {
                "name": "case-one",
                "family": "bug-fix",
                "passed": True,
                "status": "completed",
                "metrics": {"steps": 4},
            }
        ]
        markdown = render_markdown_report(report)
        self.assertIn("Pass rate: 50.0%", markdown)
        self.assertIn("| case-one | bug-fix | yes |", markdown)


if __name__ == "__main__":
    unittest.main()
