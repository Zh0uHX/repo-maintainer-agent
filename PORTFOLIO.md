# Portfolio Guide

## One-sentence description

RepoAgent is a safe, observable code-maintenance Agent that plans repository tasks, performs AST-assisted inspection and bounded edits, verifies changes with real test commands, and measures its own execution trajectory.

## What to demonstrate in three minutes

1. Run `repoagent demo` and show the initial failing test.
2. Highlight AST inspection, the precise edit and the passing second test in `trace.jsonl`.
3. Open the Observatory and inspect tool counts, validation metrics and diff.
4. Restore the run and explain why compensation is independent from Git state.
5. Show one real-model benchmark report and one failure analysis.

## Resume bullet templates

Replace bracketed values only with measured numbers from your own benchmark:

- Built a repository-maintenance Agent with an explicit plan–act–observe state machine, AST-level Python symbol search, bounded file tools and test-driven self-correction; achieved **[X]%** completion across **[N]** executable maintenance tasks.
- Designed a capability-based safety layer covering path traversal, secret-file access, shell bypass, API-key propagation and failed-validation completion, with **[N]** automated tests and reversible per-run backups.
- Implemented trajectory observability and evaluation for tool selection, error rate, latency and token usage, reducing **[metric]** from **[baseline]** to **[improved]** through **[specific change]**.

Do not present the deterministic scripted Demo as a model benchmark. It verifies orchestration and tool behavior, while `repoagent eval` measures the configured model.

## Current measured evidence

The four-case symbol-navigation probe achieved 100% pass rate in both conditions. Compared with string-only retrieval, the AST-enabled condition reduced average steps from 9.50 to 8.50, average tool calls from 8.50 to 7.50, and total tokens from 65,662 to 57,412. Treat these as single-run probe results, not a general capability claim; expand the holdout and run repeated trials before using them as a headline resume metric.

## Recommended benchmark protocol

- Use 30–50 cases drawn from at least five task families: bug fixes, tests, validation, API changes and small refactors.
- Freeze the model version, endpoint, prompts, maximum steps and benchmark commit.
- Run every condition at least three times if the provider is nondeterministic.
- Report pass rate alongside tool errors, unrelated changes, steps, latency and tokens.
- Keep failed traces and categorize failures into planning, retrieval, editing, validation and policy rejection.
- Demonstrate interruption recovery: per-case atomic checkpoints, structured error artifacts, configuration-validated resume, and fail-fast quota protection.
- Compare at least one baseline, such as string-only search versus AST-assisted search.
- Use hidden tests for implementation tasks and mutation checks for test-writing tasks.

## Interview discussion points

- Why single-step trajectories improve observability but increase latency
- Why allowlisted test commands still require OS-level isolation
- How exact replacement trades refactoring power for deterministic safety
- Why final-state and trajectory evaluation answer different questions
- When a workflow should remain deterministic instead of becoming more agentic
- How to introduce Git worktrees, queues and human approval without weakening the policy boundary
