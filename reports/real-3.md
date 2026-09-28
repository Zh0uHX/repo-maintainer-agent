# RepoAgent Benchmark Report

> Generated from executable JSONL cases. A passing case requires both Agent completion and all deterministic file assertions to pass.

## Summary

- Model: deepseek-flash
- Provider model: deepseek-flash
- AST tools: enabled
- Context retrieval: enabled
- Cases: 3
- Passed: 3
- Pass rate: 100.0%
- Average steps: 11.0
- Average tool calls: 10.0
- Tool errors: 0
- Model errors: 0
- Provider request attempts: 40
- JSON repair retries: 4
- AST tool calls: 4
- Total tokens: 209764

### Localization (n=3)

- file_acc@1: 100.0%
- file_acc@3: 100.0%
- file_acc@5: 100.0%
- function_recall@1: 66.7%
- function_recall@3: 66.7%
- function_recall@5: 66.7%

## Cases

| Case | Family | Passed | Status | Steps | Tool calls | Tokens |
|---|---|---:|---|---:|---:|---:|
| pydata__xarray-4248 | small | yes | completed | 13 | 12 | 89148 |
| scikit-learn__scikit-learn-15535 | medium | yes | completed | 12 | 11 | 86502 |
| django__django-11001 | large | yes | completed | 8 | 7 | 34114 |

## Task families

| Family | Passed | Total | Pass rate |
|---|---:|---:|---:|
| large | 1 | 1 | 100.0% |
| medium | 1 | 1 | 100.0% |
| small | 1 | 1 | 100.0% |

## Interpretation

Results depend on the selected model, endpoint, prompt version, and case set. Do not compare reports unless these inputs are held constant.
