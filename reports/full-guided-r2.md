# RepoAgent Benchmark Report

> Generated from executable JSONL cases. A passing case requires Agent completion and all deterministic assertions; a localization case passes when its top-ranked location names a gold function.

## Summary

- Model: deepseek-flash
- Provider model: deepseek-flash
- AST tools: enabled
- Context retrieval: enabled
- AST guidance prompt: on
- Cases: 44
- Passed: 34
- Pass rate: 77.3%
- Average steps: 10.89
- Average tool calls: 9.73
- Tool errors: 15
- Model errors: 1
- Provider request attempts: 605
- JSON repair retries: 38
- Locally closed brackets: 16
- AST tool calls: 107
- Total tokens: 3402260

### Localization (n=43)

- function_recall@1: 62.6%
- function_recall@3: 74.0%
- function_recall@5: 74.0%
- file_acc@1: 90.7%
- file_acc@3: 90.7%
- file_acc@5: 90.7%

## Cases

| Case | Family | Passed | Status | Steps | Tool calls | Tokens |
|---|---|---:|---|---:|---:|---:|
| pydata__xarray-4248 | small | no | completed | 7 | 6 | 72706 |
| pallets__flask-5063 | small | yes | completed | 12 | 11 | 70658 |
| psf__requests-2148 | small | yes | completed | 14 | 13 | 125094 |
| mwaskom__seaborn-3010 | small | no | completed | 4 | 3 | 20394 |
| psf__requests-2674 | small | yes | completed | 15 | 14 | 126296 |
| pallets__flask-4992 | small | yes | completed | 8 | 7 | 41174 |
| mwaskom__seaborn-2848 | small | no | completed | 16 | 15 | 143446 |
| pallets__flask-4045 | small | yes | completed | 8 | 7 | 53687 |
| psf__requests-863 | small | yes | completed | 12 | 11 | 96749 |
| psf__requests-2317 | small | yes | completed | 12 | 11 | 60616 |
| psf__requests-3362 | small | yes | completed | 10 | 9 | 48390 |
| pydata__xarray-3364 | small | yes | completed | 13 | 12 | 92930 |
| pydata__xarray-4094 | small | yes | completed | 8 | 7 | 52125 |
| psf__requests-1963 | small | yes | completed | 6 | 5 | 25840 |
| scikit-learn__scikit-learn-15535 | medium | yes | completed | 8 | 7 | 84883 |
| scikit-learn__scikit-learn-11040 | medium | yes | completed | 6 | 5 | 56063 |
| scikit-learn__scikit-learn-14092 | medium | yes | completed | 16 | 15 | 98224 |
| pytest-dev__pytest-6116 | medium | yes | completed | 16 | 15 | 104760 |
| scikit-learn__scikit-learn-10508 | medium | yes | completed | 6 | 5 | 25027 |
| sphinx-doc__sphinx-7686 | medium | no | failed | 18 | 13 | 123317 |
| astropy__astropy-6938 | medium | yes | completed | 15 | 14 | 86782 |
| scikit-learn__scikit-learn-10949 | medium | yes | completed | 8 | 7 | 64050 |
| scikit-learn__scikit-learn-10297 | medium | yes | completed | 4 | 3 | 25189 |
| pytest-dev__pytest-5221 | medium | yes | completed | 7 | 6 | 31986 |
| pytest-dev__pytest-7373 | medium | yes | completed | 8 | 7 | 35220 |
| sphinx-doc__sphinx-8282 | medium | yes | completed | 12 | 11 | 108206 |
| pytest-dev__pytest-7432 | medium | yes | completed | 7 | 6 | 35548 |
| sphinx-doc__sphinx-8435 | medium | yes | completed | 16 | 15 | 145856 |
| sphinx-doc__sphinx-8273 | medium | yes | completed | 13 | 12 | 63866 |
| django__django-14238 | large | yes | completed | 13 | 12 | 102624 |
| django__django-12915 | large | yes | completed | 11 | 10 | 50077 |
| matplotlib__matplotlib-25442 | large | no | failed | 18 | 15 | 134985 |
| sympy__sympy-17630 | large | no | error | 0 | 0 | 22883 |
| django__django-11099 | large | yes | completed | 5 | 4 | 13142 |
| sympy__sympy-23117 | large | no | completed | 8 | 7 | 84769 |
| django__django-14730 | large | no | failed | 18 | 15 | 133175 |
| django__django-14752 | large | yes | completed | 11 | 10 | 61437 |
| sympy__sympy-16503 | large | yes | completed | 15 | 14 | 148643 |
| django__django-10914 | large | yes | completed | 16 | 15 | 93054 |
| sympy__sympy-13895 | large | no | completed | 17 | 16 | 212379 |
| django__django-13768 | large | yes | completed | 6 | 5 | 27875 |
| django__django-11001 | large | no | completed | 14 | 13 | 63994 |
| sympy__sympy-12454 | large | yes | completed | 11 | 10 | 57418 |
| sympy__sympy-20154 | large | yes | completed | 11 | 10 | 76723 |

## Errors

- `sympy__sympy-17630`: RuntimeError: Model request failed after retries: Model returned an empty message.

## Task families

| Family | Passed | Total | Pass rate |
|---|---:|---:|---:|
| large | 9 | 15 | 60.0% |
| medium | 14 | 15 | 93.3% |
| small | 11 | 14 | 78.6% |

## Interpretation

Results depend on the selected model, endpoint, prompt version, and case set. Do not compare reports unless these inputs are held constant.
