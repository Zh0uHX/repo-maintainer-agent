# RepoAgent Benchmark Report

> Generated from executable JSONL cases. A passing case requires both Agent completion and all deterministic file assertions to pass.

## Summary

- Model: deepseek-chat
- AST tools: enabled
- Cases: 10
- Passed: 10
- Pass rate: 100.0%
- Average steps: 6.9
- Average tool calls: 5.9
- Tool errors: 0
- Total tokens: 95906

## Cases

| Case | Family | Passed | Status | Steps | Tool calls | Tokens |
|---|---|---:|---|---:|---:|---:|
| discount-percentage | bug-fix | yes | completed | 7 | 6 | 8888 |
| inclusive-range-boundary | bug-fix | yes | completed | 7 | 6 | 7467 |
| validate-network-port | input-validation | yes | completed | 7 | 6 | 10056 |
| validate-pagination | input-validation | yes | completed | 7 | 6 | 9767 |
| redact-user-password | api-contract | yes | completed | 7 | 6 | 9231 |
| normalize-account-status | api-contract | yes | completed | 6 | 5 | 8165 |
| add-safe-divide-tests | test-addition | yes | completed | 5 | 4 | 6451 |
| add-parse-bool-tests | test-addition | yes | completed | 5 | 4 | 7539 |
| rename-display-name-api | cross-file-refactor | yes | completed | 9 | 8 | 13979 |
| extract-shared-display-name | cross-file-refactor | yes | completed | 9 | 8 | 14363 |

## Task families

| Family | Passed | Total | Pass rate |
|---|---:|---:|---:|
| api-contract | 2 | 2 | 100.0% |
| bug-fix | 2 | 2 | 100.0% |
| cross-file-refactor | 2 | 2 | 100.0% |
| input-validation | 2 | 2 | 100.0% |
| test-addition | 2 | 2 | 100.0% |

## Interpretation

Results depend on the selected model, endpoint, prompt version, and case set. Do not compare reports unless these inputs are held constant.
