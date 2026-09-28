from __future__ import annotations

from typing import Any

LOCALIZATION_METRICS = ("function_recall@1", "function_recall@5", "file_acc@1")


def _metric(report: dict[str, Any], name: str) -> float:
    if name in LOCALIZATION_METRICS:
        value = (report.get("localization") or {}).get(name)
    else:
        value = report.get(name)
    return float(value or 0)


def compare_reports(baseline: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    metrics = (
        "pass_rate",
        "average_steps",
        "average_tool_calls",
        "tool_errors",
        "ast_tool_calls",
        "context_retrieval_calls",
        "total_tokens",
        *LOCALIZATION_METRICS,
    )
    deltas = {
        name: round(_metric(candidate, name) - _metric(baseline, name), 4) for name in metrics
    }
    metric_values = {
        name: {
            "baseline": _metric(baseline, name),
            "candidate": _metric(candidate, name),
            "delta": deltas[name],
            "relative_delta": _relative_delta(_metric(baseline, name), _metric(candidate, name)),
        }
        for name in metrics
    }
    families = {}
    family_names = sorted(set(baseline.get("families", {})) | set(candidate.get("families", {})))
    for family in family_names:
        before = baseline.get("families", {}).get(family, {}).get("pass_rate", 0)
        after = candidate.get("families", {}).get(family, {}).get("pass_rate", 0)
        families[family] = {
            "baseline_pass_rate": before,
            "candidate_pass_rate": after,
            "delta": round(float(after) - float(before), 4),
        }
    configured_model_match = baseline.get("model") == candidate.get("model")
    provider_model_match = set(baseline.get("provider_models", [])) == set(
        candidate.get("provider_models", [])
    )
    case_count_match = baseline.get("total") == candidate.get("total")
    baseline_ast = baseline.get("ast_enabled")
    candidate_ast = candidate.get("ast_enabled")
    baseline_context = baseline.get("context_retrieval_enabled", False)
    candidate_context = candidate.get("context_retrieval_enabled", False)
    baseline_guidance = bool(baseline.get("ast_guidance"))
    candidate_guidance = bool(candidate.get("ast_guidance"))
    ast_condition_match = baseline_ast == candidate_ast
    context_retrieval_match = baseline_context == candidate_context
    guidance_match = baseline_guidance == candidate_guidance
    baseline_case_names = [str(item.get("name")) for item in baseline.get("results", [])]
    candidate_case_names = [str(item.get("name")) for item in candidate.get("results", [])]
    case_names_match = (
        baseline_case_names == candidate_case_names
        and len(baseline_case_names) == int(baseline.get("total", 0))
        and len(candidate_case_names) == int(candidate.get("total", 0))
    )
    ast_contrast_valid = (
        baseline_ast is False
        and candidate_ast is True
        and context_retrieval_match
        and guidance_match
    )
    context_contrast_valid = (
        baseline_context is False
        and candidate_context is True
        and ast_condition_match
        and guidance_match
    )
    guidance_contrast_valid = (
        not baseline_guidance
        and candidate_guidance
        and candidate_ast is True
        and ast_condition_match
        and context_retrieval_match
    )
    comparison_dimension = (
        "ast"
        if ast_contrast_valid
        else "context_retrieval"
        if context_contrast_valid
        else "ast_guidance"
        if guidance_contrast_valid
        else "invalid"
    )
    tool_condition_valid = ast_contrast_valid or context_contrast_valid or guidance_contrast_valid
    comparison_valid = (
        configured_model_match
        and provider_model_match
        and case_count_match
        and case_names_match
        and tool_condition_valid
    )
    candidate_by_name = {str(item.get("name")): item for item in candidate.get("results", [])}
    case_comparisons = []
    for baseline_result in baseline.get("results", []):
        name = str(baseline_result.get("name"))
        candidate_result = candidate_by_name.get(name, {})
        baseline_metrics = baseline_result.get("metrics", {})
        candidate_metrics = candidate_result.get("metrics", {})
        case_comparisons.append(
            {
                "name": name,
                "baseline_passed": bool(baseline_result.get("passed")),
                "candidate_passed": bool(candidate_result.get("passed")),
                "baseline_steps": int(baseline_metrics.get("steps", 0)),
                "candidate_steps": int(candidate_metrics.get("steps", 0)),
                "baseline_tool_calls": int(baseline_metrics.get("tool_calls", 0)),
                "candidate_tool_calls": int(candidate_metrics.get("tool_calls", 0)),
                "baseline_tokens": int(baseline_metrics.get("total_tokens", 0)),
                "candidate_tokens": int(candidate_metrics.get("total_tokens", 0)),
            }
        )
    return {
        "model_match": configured_model_match and provider_model_match,
        "configured_model_match": configured_model_match,
        "provider_model_match": provider_model_match,
        "case_count_match": case_count_match,
        "case_names_match": case_names_match,
        "ast_condition_match": ast_condition_match,
        "ast_contrast_valid": ast_contrast_valid,
        "context_retrieval_match": context_retrieval_match,
        "context_contrast_valid": context_contrast_valid,
        "guidance_contrast_valid": guidance_contrast_valid,
        "comparison_dimension": comparison_dimension,
        "comparison_valid": comparison_valid,
        "baseline": {
            "model": baseline.get("model"),
            "ast_enabled": baseline_ast,
            "context_retrieval_enabled": baseline_context,
            "ast_guidance": baseline_guidance,
            "total": baseline.get("total", 0),
        },
        "candidate": {
            "model": candidate.get("model"),
            "ast_enabled": candidate_ast,
            "context_retrieval_enabled": candidate_context,
            "ast_guidance": candidate_guidance,
            "total": candidate.get("total", 0),
        },
        "deltas": deltas,
        "metrics": metric_values,
        "families": families,
        "cases": case_comparisons,
    }


def render_comparison_markdown(comparison: dict[str, Any]) -> str:
    baseline = comparison["baseline"]
    candidate = comparison["candidate"]
    baseline_label, candidate_label = _condition_labels(comparison["comparison_dimension"])
    lines = [
        "# RepoAgent Ablation Comparison",
        "",
        (
            "- Machine-checkable comparison valid: "
            f"{'yes' if comparison['comparison_valid'] else 'no'}"
        ),
        f"- Configured model match: {'yes' if comparison['configured_model_match'] else 'no'}",
        f"- Provider model match: {'yes' if comparison['provider_model_match'] else 'no'}",
        f"- Case count match: {'yes' if comparison['case_count_match'] else 'no'}",
        f"- Exact case order match: {'yes' if comparison['case_names_match'] else 'no'}",
        f"- Ablation dimension: {comparison['comparison_dimension']}",
        f"- Baseline AST: {baseline.get('ast_enabled')}",
        f"- Candidate AST: {candidate.get('ast_enabled')}",
        f"- Baseline context retrieval: {baseline.get('context_retrieval_enabled')}",
        f"- Candidate context retrieval: {candidate.get('context_retrieval_enabled')}",
        f"- Baseline AST guidance: {baseline.get('ast_guidance')}",
        f"- Candidate AST guidance: {candidate.get('ast_guidance')}",
        f"- Cases: {baseline.get('total')} → {candidate.get('total')}",
        "",
        "## Aggregate results",
        "",
        f"| Metric | {baseline_label} | {candidate_label} | Observed change |",
        "|---|---:|---:|---:|",
        _metric_row("Pass rate", comparison["metrics"]["pass_rate"], percentage=True),
        *(
            _metric_row(name, comparison["metrics"][name], percentage=True)
            for name in LOCALIZATION_METRICS
            if comparison["metrics"][name]["baseline"] or comparison["metrics"][name]["candidate"]
        ),
        _metric_row("Average steps", comparison["metrics"]["average_steps"], digits=2),
        _metric_row("Average tool calls", comparison["metrics"]["average_tool_calls"], digits=2),
        _metric_row("Tool errors", comparison["metrics"]["tool_errors"]),
        _metric_row("AST tool calls", comparison["metrics"]["ast_tool_calls"]),
        _metric_row("Context retrieval calls", comparison["metrics"]["context_retrieval_calls"]),
        _metric_row("Total tokens", comparison["metrics"]["total_tokens"]),
        "",
        "## Task families",
        "",
        "| Family | Baseline | Candidate | Delta |",
        "|---|---:|---:|---:|",
    ]
    for family, values in comparison["families"].items():
        lines.append(
            f"| {family} | {values['baseline_pass_rate']:.1%} | "
            f"{values['candidate_pass_rate']:.1%} | {values['delta']:+.1%} |"
        )
    lines.extend(
        [
            "",
            "## Per-case results",
            "",
            "| Case | Passed | Steps | Tool calls | Tokens |",
            "|---|---:|---:|---:|---:|",
        ]
    )
    for case in comparison["cases"]:
        name = case["name"].replace("|", "\\|")
        lines.append(
            f"| {name} | {_yes_no(case['baseline_passed'])} → "
            f"{_yes_no(case['candidate_passed'])} | "
            f"{case['baseline_steps']} → {case['candidate_steps']} | "
            f"{case['baseline_tool_calls']} → {case['candidate_tool_calls']} | "
            f"{case['baseline_tokens']:,} → {case['candidate_tokens']:,} |"
        )
    lines.extend(
        [
            "",
            (
                "> Treat the comparison as causal only when model, case set, prompts, step budget, "
                "and repeated-run protocol are held constant."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def _relative_delta(baseline: float, candidate: float) -> float | None:
    if baseline == 0:
        return None
    return round((candidate - baseline) / abs(baseline), 4)


def _metric_row(
    label: str, values: dict[str, Any], *, percentage: bool = False, digits: int = 0
) -> str:
    baseline = float(values["baseline"])
    candidate = float(values["candidate"])
    delta = float(values["delta"])
    relative = values["relative_delta"]
    if percentage:
        return f"| {label} | {baseline:.1%} | {candidate:.1%} | {delta * 100:+.1f} pp |"
    change = f"{delta:+,.{digits}f}"
    if relative is not None:
        change += f" ({float(relative):+.1%})"
    return f"| {label} | {baseline:,.{digits}f} | {candidate:,.{digits}f} | {change} |"


def _yes_no(value: bool) -> str:
    return "yes" if value else "no"


def _condition_labels(dimension: str) -> tuple[str, str]:
    if dimension == "ast":
        return "String baseline", "AST candidate"
    if dimension == "context_retrieval":
        return "Context disabled", "Context enabled"
    if dimension == "ast_guidance":
        return "Default prompt", "AST-guided prompt"
    return "Baseline", "Candidate"
