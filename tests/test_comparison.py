import unittest

from repoagent.comparison import compare_reports, render_comparison_markdown


class ComparisonTests(unittest.TestCase):
    def test_compares_overall_and_family_metrics(self):
        baseline = {
            "model": "same-model",
            "provider_models": ["actual-model"],
            "ast_enabled": False,
            "total": 10,
            "pass_rate": 0.6,
            "average_steps": 9,
            "average_tool_calls": 8,
            "tool_errors": 3,
            "ast_tool_calls": 0,
            "total_tokens": 1000,
            "families": {"bug-fix": {"pass_rate": 0.5}},
            "results": [{"name": f"case-{index}"} for index in range(10)],
        }
        candidate = {
            "model": "same-model",
            "provider_models": ["actual-model"],
            "ast_enabled": True,
            "total": 10,
            "pass_rate": 0.8,
            "average_steps": 7,
            "average_tool_calls": 6,
            "tool_errors": 1,
            "ast_tool_calls": 4,
            "total_tokens": 900,
            "families": {"bug-fix": {"pass_rate": 1.0}},
            "results": [{"name": f"case-{index}"} for index in range(10)],
        }
        result = compare_reports(baseline, candidate)
        self.assertAlmostEqual(result["deltas"]["pass_rate"], 0.2)
        self.assertTrue(result["comparison_valid"])
        self.assertEqual(result["comparison_dimension"], "ast")
        self.assertEqual(result["families"]["bug-fix"]["delta"], 0.5)
        self.assertEqual(result["deltas"]["ast_tool_calls"], 4)
        markdown = render_comparison_markdown(result)
        self.assertIn("+20.0 pp", markdown)
        self.assertIn("bug-fix", markdown)

    def test_rejects_different_case_order_or_wrong_ast_direction(self):
        baseline = {
            "model": "m",
            "provider_models": ["p"],
            "ast_enabled": True,
            "total": 2,
            "results": [{"name": "a"}, {"name": "b"}],
        }
        candidate = {
            "model": "m",
            "provider_models": ["p"],
            "ast_enabled": False,
            "total": 2,
            "results": [{"name": "b"}, {"name": "a"}],
        }

        result = compare_reports(baseline, candidate)

        self.assertFalse(result["case_names_match"])
        self.assertFalse(result["ast_contrast_valid"])
        self.assertFalse(result["comparison_valid"])

    def test_accepts_context_retrieval_ablation_with_ast_held_constant(self):
        shared = {
            "model": "m",
            "provider_models": ["p"],
            "ast_enabled": True,
            "total": 1,
            "results": [{"name": "retrieval-case"}],
        }
        baseline = {**shared, "context_retrieval_enabled": False}
        candidate = {
            **shared,
            "context_retrieval_enabled": True,
            "context_retrieval_calls": 3,
        }

        result = compare_reports(baseline, candidate)
        markdown = render_comparison_markdown(result)

        self.assertTrue(result["comparison_valid"])
        self.assertTrue(result["context_contrast_valid"])
        self.assertEqual(result["comparison_dimension"], "context_retrieval")
        self.assertIn("Context disabled", markdown)
        self.assertIn("Context retrieval calls", markdown)


if __name__ == "__main__":
    unittest.main()
