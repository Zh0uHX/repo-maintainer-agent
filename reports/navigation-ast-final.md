# RepoAgent Benchmark Report

> Generated from executable JSONL cases. A passing case requires both Agent completion and all deterministic file assertions to pass.

## Summary

- Model: deepseek-chat
- Provider model: deepseek-v4-flash
- AST tools: enabled
- Cases: 4
- Passed: 4
- Pass rate: 100.0%
- Average steps: 8.5
- Average tool calls: 7.5
- Tool errors: 0
- AST tool calls: 6
- Total tokens: 57412

## Cases

| Case | Family | Passed | Status | Steps | Tool calls | Tokens |
|---|---|---:|---|---:|---:|---:|
| locate-invoice-total-method | symbol-navigation | yes | completed | 9 | 8 | 13280 |
| locate-user-repository-lookup | symbol-navigation | yes | completed | 6 | 5 | 8381 |
| rename-token-store-method | symbol-navigation | yes | completed | 13 | 12 | 25335 |
| locate-cache-falsey-value-bug | symbol-navigation | yes | completed | 6 | 5 | 10416 |

## Task families

| Family | Passed | Total | Pass rate |
|---|---:|---:|---:|
| symbol-navigation | 4 | 4 | 100.0% |

## Interpretation

Results depend on the selected model, endpoint, prompt version, and case set. Do not compare reports unless these inputs are held constant.
