# Evaluation Protocol

## Goal

Measure whether RepoAgent completes repository tasks correctly, stays within the requested change scope, uses tools reliably, and does so at acceptable latency and token cost.

## Case structure

Each JSONL case may define:

| Field | Purpose |
|---|---|
| `family` | Task-family aggregation |
| `files` | Repository state visible to the Agent |
| `hidden_files` | Tests injected only after Agent completion |
| `contains` / `not_contains` | Minimal structural assertions |
| `allowed_changed_files` | Scope-control assertion |
| `check_commands` | Independent final-state verification |
| `mutations` | Faults that newly added tests must detect |

An Agent self-reported `completed` result is insufficient. A case passes only if all deterministic assertions and independent checks pass.

## Checkpointing and recovery

The evaluator atomically rewrites JSON and Markdown reports after every case. A model, provider, or harness exception becomes a structured `status: error` result; when `--artifacts` is set, the temporary repository, trace, and `evaluation-error.json` are preserved. The default is fail-fast on infrastructure errors to avoid wasting provider quota.

Resume the same suite after correcting an external failure:

```bash
repoagent eval evals/pilot.jsonl \
  --output reports/pilot-ast.json \
  --markdown reports/pilot-ast.md \
  --artifacts reports/pilot-ast-artifacts \
  --resume
```

Resume validates the configured model and AST mode, skips completed cases, and retries error cases. Use `--continue-on-error` only when collecting all infrastructure failures is worth the additional calls.

## Pilot suite

`evals/pilot.jsonl` contains ten cases across five equally weighted families:

- Bug fixes
- Input validation
- API contracts and secret redaction
- Test additions with mutation checks
- Cross-file refactors

Run AST-enabled evaluation:

```bash
repoagent eval evals/pilot.jsonl \
  --output reports/pilot-ast.json \
  --markdown reports/pilot-ast.md \
  --artifacts reports/pilot-ast-artifacts
```

Run the string-search baseline with the same model and case set:

```bash
repoagent eval evals/pilot.jsonl \
  --disable-ast \
  --output reports/pilot-string.json \
  --markdown reports/pilot-string.md \
  --artifacts reports/pilot-string-artifacts
```

Compare reports:

```bash
repoagent compare reports/pilot-string.json reports/pilot-ast.json \
  --output reports/ablation.md
```

## Valid comparison requirements

- Same exact model identifier and provider endpoint
- Same benchmark commit and case order
- Same prompts, maximum steps and command policy
- Same temperature and response format
- At least three repeated runs for nondeterministic providers
- No manual repair between cases

The current client uses temperature zero, but providers may still be nondeterministic.

## AST navigation probe

The general pilot can be solved through direct file inspection, so it validates task reliability but may not exercise AST tools. `evals/navigation.jsonl` contains four named-symbol tasks with distractor definitions. Run this smaller probe before paying for a full baseline:

```bash
repoagent eval evals/navigation.jsonl \
  --output reports/navigation-ast.json \
  --markdown reports/navigation-ast.md \
  --artifacts reports/navigation-ast-artifacts
```

Only run the `--disable-ast` counterpart if the AST-enabled report records nonzero `ast_tool_calls`.

Retry one corrected or transiently failed case without paying for the full suite, then merge it back by case name:

```bash
repoagent eval evals/navigation.jsonl --case CASE_NAME \
  --output reports/retry.json --markdown reports/retry.md
repoagent merge reports/navigation-ast.json reports/retry.json \
  --output reports/navigation-ast-final.json \
  --markdown reports/navigation-ast-final.md
```

## Context-retrieval probe

`evals/context_retrieval.jsonl` contains four behavior-described tasks that do not name the target symbol. Hold AST availability constant and vary only the ranked context tool:

```bash
repoagent eval evals/context_retrieval.jsonl \
  --disable-context \
  --output reports/context-disabled.json \
  --markdown reports/context-disabled.md \
  --artifacts reports/context-disabled-artifacts

repoagent eval evals/context_retrieval.jsonl \
  --output reports/context-enabled.json \
  --markdown reports/context-enabled.md \
  --artifacts reports/context-enabled-artifacts

repoagent compare reports/context-disabled.json reports/context-enabled.json \
  --output reports/context-ablation.md
```

The comparison command accepts exactly one forward tool contrast at a time: AST disabled→enabled with context held constant, or context retrieval disabled→enabled with AST held constant. Model, provider model, exact case order and case count must also match.

## Real-repository suite (SWE-bench Lite)

Synthetic fixtures contain three to five small files, so there is nothing for symbol navigation
to navigate. The real-repository suite replaces inline `files` with a pinned upstream tree:

```json
{"name": "psf__requests-2317", "instance_id": "psf__requests-2317", "family": "small",
 "mode": "localize", "repo": "psf/requests", "base_commit": "091991be...",
 "task": "<problem_statement>", "gold": {"files": [...], "functions": [...]},
 "meta": {"python_files": 41, "hunks": 1}}
```

The harness keeps one bare, blob-less clone per repository in `~/.cache/repoagent-repos`
(override with `REPOAGENT_REPO_CACHE`) and materializes each case with `git archive`, so the
Agent never sees `.git` or any later history. Artifacts keep only `.repoagent/` run records.

### Dataset facts that constrain the design

Checked against all 300 SWE-bench Lite test instances:

- Every gold patch edits exactly one file; hunk counts are 1 / 2 / 3 for 190 / 73 / 37 cases.
- Repositories: django 114, sympy 77, matplotlib 23, scikit-learn 23, pytest 17, sphinx 16,
  astropy 6, requests 6, pylint 6, xarray 5, seaborn 4, flask 3.

Cross-file and test-writing task families therefore cannot be drawn from Lite. The suite is
stratified by repository size instead (Python files at `base_commit`: small < 150,
medium 150–800, large > 800), round-robin over hunk count, with at most eight cases per
repository. `scripts/select_cases.py` is deterministic for a given `--seed`.

### Two evaluation layers

| Layer | Mode | Judge | Needs repo environment |
|---|---|---|---|
| Localization | `localize`: Agent cannot edit and must finish with ranked `locations` | File Acc@1/3/5 and function recall@1/3/5 against locations parsed from the gold patch | No |
| Resolution | `edit`: Agent edits normally; `--predictions` exports SWE-bench prediction JSONL | Official SWE-bench harness (`FAIL_TO_PASS` / `PASS_TO_PASS`) | Yes, outside this harness |

A localization case passes when the Agent completes and its top-ranked location names a gold
function; cases whose gold patch touches no function fall back to the top-ranked file. The
headline metric is `function_recall@1`. File Acc@1 saturated at 9/10 in the first real-repo
baseline because every Lite patch edits a single file, so it no longer separates conditions.
Gold functions are the innermost function or class enclosing each removed line, or the line
preceding each insertion, at `base_commit`. An insertion placed between two top-level
definitions is attributed to the preceding definition or, when it lands on a blank line between
definitions, to no symbol; such cases (2 of 44 in the default suite) are scored at file level
only and report `function_recall@k` as `null`.

Real-repository cases disable `run_check` by default because no environment is installed.
Hidden tests and mutation checks apply only to fixture suites; do not describe localization
results as test-verified.

Known limitation: `retrieve_context` indexes at most 240 files in directory order, so on
medium and large repositories it only sees an alphabetical prefix of the tree unless the Agent
passes a narrower `glob`. Record this before comparing context-enabled and disabled conditions.

### Model protocol recovery

The first ten-case baseline lost 3 of 10 cases to protocol failures, not localization:

- Nested `finish` replies missing their final `}`. Regenerating repeated the same mistake three
  times, so the client now appends missing closers when the reply ends outside a string with
  unclosed brackets (`closed_brackets` in metrics).
- Whitespace-only replies in JSON mode, typically in the plan stage. The client resends the
  original request and drops `response_format` after the first empty reply
  (`json_mode_fallback` in the trace).

Report both counters with any result so recovered cases are not mistaken for clean runs.

## Metrics

- Task completion and per-family pass rate
- Hidden-test success
- Allowed-change compliance
- Mutation kill success for test-writing tasks
- Tool errors and tool-call distribution
- Provider request attempts, model errors, JSON repair retries, and retry-inclusive token usage
- Context-retrieval calls and an explicit `context_retrieval_enabled` condition flag
- Agent validation versus independent validation
- Steps, model calls, latency and token usage

## Failure taxonomy

Preserved failed artifacts should be classified as:

1. Planning: wrong or incomplete task decomposition
2. Retrieval: failed to locate relevant code or callers
3. Editing: rejected, ambiguous or incorrect change
4. Validation: missing, wrong or misinterpreted checks
5. Scope: unrelated or forbidden files changed
6. Policy: safe action rejected or unsafe action attempted
7. Model protocol: malformed JSON or invalid tool arguments

Do not tune prompts against hidden tests. Promote recurring failures into new public training cases or general tool improvements, then evaluate on a separate holdout set.
