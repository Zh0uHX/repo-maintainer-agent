# RepoAgent Benchmark Report

> Generated from executable JSONL cases. A passing case requires Agent completion and all deterministic assertions; a localization case passes when its top-ranked location names a gold function.

## Summary

- Model: deepseek-flash
- Provider model: deepseek-flash
- AST tools: enabled
- Context retrieval: enabled
- AST guidance prompt: on
- Cases: 10
- Passed: 7
- Pass rate: 70.0%
- Average steps: 9.4
- Average tool calls: 8.3
- Tool errors: 1
- Model errors: 0
- Provider request attempts: 124
- JSON repair retries: 9
- Locally closed brackets: 3
- AST tool calls: 21
- Total tokens: 682847

### Localization (n=10)

- function_recall@1: 52.2%
- function_recall@3: 68.9%
- function_recall@5: 68.9%
- file_acc@1: 90.0%
- file_acc@3: 90.0%
- file_acc@5: 90.0%

## Cases

| Case | Family | Passed | Status | Steps | Tool calls | Tokens |
|---|---|---:|---|---:|---:|---:|
| pallets__flask-5063 | small | yes | completed | 8 | 7 | 55178 |
| psf__requests-2148 | small | no | completed | 8 | 7 | 64195 |
| mwaskom__seaborn-3010 | small | no | completed | 5 | 4 | 24228 |
| scikit-learn__scikit-learn-11040 | medium | yes | completed | 6 | 5 | 43355 |
| scikit-learn__scikit-learn-14092 | medium | yes | completed | 8 | 7 | 60454 |
| pytest-dev__pytest-6116 | medium | yes | completed | 11 | 10 | 76229 |
| django__django-14238 | large | yes | completed | 12 | 11 | 80399 |
| django__django-12915 | large | yes | completed | 12 | 10 | 51406 |
| matplotlib__matplotlib-25442 | large | yes | completed | 12 | 11 | 106681 |
| sympy__sympy-17630 | large | no | completed | 12 | 11 | 120722 |

## Task families

| Family | Passed | Total | Pass rate |
|---|---:|---:|---:|
| large | 3 | 4 | 75.0% |
| medium | 3 | 3 | 100.0% |
| small | 1 | 3 | 33.3% |

## Interpretation

Results depend on the selected model, endpoint, prompt version, and case set. Do not compare reports unless these inputs are held constant.
