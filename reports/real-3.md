# RepoAgent Benchmark Report

> Generated from executable JSONL cases. A passing case requires Agent completion and all deterministic assertions; a localization case passes when its top-ranked location names a gold function.

## Summary

- Model: deepseek-flash
- Provider model: deepseek-flash
- AST tools: enabled
- Context retrieval: enabled
- AST guidance prompt: off
- Cases: 3
- Passed: 2
- Pass rate: 66.7%
- Average steps: 11.0
- Average tool calls: 10.0
- Tool errors: 0
- Model errors: 0
- Provider request attempts: 40
- JSON repair retries: 4
- Locally closed brackets: 0
- AST tool calls: 4
- Total tokens: 209764

### Localization (n=3)

- function_recall@1: 66.7%
- function_recall@3: 66.7%
- function_recall@5: 66.7%
- file_acc@1: 100.0%
- file_acc@3: 100.0%
- file_acc@5: 100.0%

## Cases

| Case | Family | Passed | Status | Steps | Tool calls | Tokens |
|---|---|---:|---|---:|---:|---:|
| pydata__xarray-4248 | small | no | completed | 13 | 12 | 89148 |
| scikit-learn__scikit-learn-15535 | medium | yes | completed | 12 | 11 | 86502 |
| django__django-11001 | large | yes | completed | 8 | 7 | 34114 |

## Task families

| Family | Passed | Total | Pass rate |
|---|---:|---:|---:|
| large | 1 | 1 | 100.0% |
| medium | 1 | 1 | 100.0% |
| small | 0 | 1 | 0.0% |

## Interpretation

Results depend on the selected model, endpoint, prompt version, and case set. Do not compare reports unless these inputs are held constant.
