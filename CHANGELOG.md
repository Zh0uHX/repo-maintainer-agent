# Changelog

## Unreleased

- Added real-repository evaluation: cached blob-less clones, `git archive` workspaces, and a
  44-case SWE-bench Lite localization suite stratified by repository size.
- Added `localize` task mode with ranked locations scored by file Acc@k and function recall@k.
- Added SWE-bench prediction export for edit-mode real-repository cases.
- Cached parsed Python symbols by mtime; replaced the plan-stage file listing with a
  directory-level repository overview.
- Added remaining-step notices and elision of all but the newest six observation bodies.
- Closed brackets that a model drops at the end of a nested reply locally instead of asking it to
  regenerate; counted as `closed_brackets`.
- Resent the original request after whitespace-only replies, without JSON mode after the first;
  recorded as `json_mode_fallback`. Traces now keep the last unparseable reply and `finish_reason`.
- Added per-result `summary` and `scripts/failure_report.py` for deterministic failure labels.
- Made a top-1 gold function hit the localization pass rule and `function_recall@1` the headline
  metric; file Acc@k is secondary because Lite patches always edit a single file.
- Added `--ast-guidance`, an AST-first localization workflow in the prompt, recorded in reports,
  enforced on resume and merge, and supported by `compare` as its own dimension.

## 0.4.0

- Added bounded repository context retrieval over paths, identifiers, AST symbols and code chunks.
- Added context-retrieval capability flags to CLI, API, benchmark provenance and comparisons.
- Added retrieval ranking, sensitive-file exclusion and configuration regression tests.
- Added a source-backed `repoagent --version` command and public-report curation guidance.
- Added an explicit structured-output token ceiling to reduce truncated provider JSON responses.

## 0.3.0

- Added hidden benchmark fixtures and independent verification checks.
- Added task-family metrics and portfolio Markdown reporting.
- Added mutation checks for test-generation tasks.
- Added a ten-case, five-family pilot benchmark.
- Added an AST-disabled string-search baseline and report comparison command.
- Added a four-case named-symbol navigation probe and aggregate AST utilization metrics.
- Added configured/provider model provenance, named-case retries and report merging.
- Added atomic per-case checkpoints, structured error artifacts, fail-fast quota protection, and resumable evaluation runs.
- Added contextual malformed-JSON repair retries with retry-inclusive usage and model-error tracing.
- Strengthened ablation validation with exact case-order and AST-direction checks plus per-case cost reporting.
- Added a reproducible evaluation and ablation protocol.

## 0.2.0

- Added Python AST inspection and qualified symbol search.
- Added trace-derived operational and token metrics.
- Added benchmark JSON and Markdown reports.
- Added deterministic zero-key end-to-end Demo.
- Added run history aggregation and Observatory dashboard.
- Added API integration tests and server-side capability gates.
- Added CI, container packaging, architecture and security documentation.

## 0.1.0

- Initial plan–act–observe Agent, guarded repository tools, CLI/API, backups, restore and JSONL evaluation harness.
