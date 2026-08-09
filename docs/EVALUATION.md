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
