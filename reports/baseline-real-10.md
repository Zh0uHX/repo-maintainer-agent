# RepoAgent Benchmark Report

> Generated from executable JSONL cases. A passing case requires Agent completion and all deterministic assertions; a localization case passes when its top-ranked location names a gold function.

## Summary

- Model: deepseek-flash
- Provider model: deepseek-flash
- AST tools: enabled
- Context retrieval: enabled
- AST guidance prompt: off
- Cases: 10
- Passed: 6
- Pass rate: 60.0%
- Average steps: 11.7
- Average tool calls: 10.7
- Tool errors: 0
- Model errors: 0
- Provider request attempts: 148
- JSON repair retries: 18
- Locally closed brackets: 2
- AST tool calls: 14
- Total tokens: 844059

### Localization (n=10)

- function_recall@1: 46.7%
- function_recall@3: 68.9%
- function_recall@5: 71.1%
- file_acc@1: 90.0%
- file_acc@3: 90.0%
- file_acc@5: 100.0%

## Cases

| Case | Family | Passed | Status | Steps | Tool calls | Tokens |
|---|---|---:|---|---:|---:|---:|
| pallets__flask-5063 | small | yes | completed | 14 | 13 | 70447 |
| psf__requests-2148 | small | yes | completed | 13 | 12 | 108056 |
| mwaskom__seaborn-3010 | small | no | completed | 4 | 3 | 20016 |
| scikit-learn__scikit-learn-11040 | medium | no | completed | 6 | 5 | 43374 |
| scikit-learn__scikit-learn-14092 | medium | yes | completed | 16 | 15 | 98024 |
| pytest-dev__pytest-6116 | medium | yes | completed | 11 | 10 | 48411 |
| django__django-14238 | large | no | completed | 15 | 14 | 86762 |
| django__django-12915 | large | yes | completed | 9 | 8 | 49617 |
| matplotlib__matplotlib-25442 | large | yes | completed | 11 | 10 | 78679 |
| sympy__sympy-17630 | large | no | completed | 18 | 17 | 240673 |

## Task families

| Family | Passed | Total | Pass rate |
|---|---:|---:|---:|
| large | 2 | 4 | 50.0% |
| medium | 2 | 3 | 66.7% |
| small | 2 | 3 | 66.7% |

## Interpretation

Results depend on the selected model, endpoint, prompt version, and case set. Do not compare reports unless these inputs are held constant.
