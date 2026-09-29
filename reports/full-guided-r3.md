# RepoAgent Benchmark Report

> Generated from executable JSONL cases. A passing case requires Agent completion and all deterministic assertions; a localization case passes when its top-ranked location names a gold function.

## Summary

- Model: deepseek-flash
- Provider model: deepseek-flash
- AST tools: enabled
- Context retrieval: enabled
- AST guidance prompt: on
- Cases: 44
- Passed: 29
- Pass rate: 65.9%
- Average steps: 10.93
- Average tool calls: 9.75
- Tool errors: 13
- Model errors: 1
- Provider request attempts: 616
- JSON repair retries: 42
- Locally closed brackets: 15
- AST tool calls: 96
- Total tokens: 3441628

### Localization (n=43)

- function_recall@1: 53.3%
- function_recall@3: 75.4%
- function_recall@5: 77.1%
- file_acc@1: 86.1%
- file_acc@3: 90.7%
- file_acc@5: 90.7%

## Cases

| Case | Family | Passed | Status | Steps | Tool calls | Tokens |
|---|---|---:|---|---:|---:|---:|
| pydata__xarray-4248 | small | no | failed | 18 | 15 | 104744 |
| pallets__flask-5063 | small | yes | completed | 12 | 11 | 44480 |
| psf__requests-2148 | small | no | completed | 13 | 12 | 114207 |
| mwaskom__seaborn-3010 | small | no | completed | 7 | 6 | 36701 |
| psf__requests-2674 | small | yes | completed | 14 | 13 | 137202 |
| pallets__flask-4992 | small | yes | completed | 8 | 7 | 30266 |
| mwaskom__seaborn-2848 | small | yes | completed | 16 | 15 | 169828 |
| pallets__flask-4045 | small | yes | completed | 12 | 11 | 76062 |
| psf__requests-863 | small | no | completed | 13 | 12 | 102325 |
| psf__requests-2317 | small | yes | completed | 12 | 11 | 78375 |
| psf__requests-3362 | small | no | completed | 12 | 10 | 70395 |
| pydata__xarray-3364 | small | no | completed | 13 | 12 | 108334 |
| pydata__xarray-4094 | small | yes | completed | 8 | 7 | 62400 |
| psf__requests-1963 | small | yes | completed | 10 | 8 | 66491 |
| scikit-learn__scikit-learn-15535 | medium | yes | completed | 13 | 12 | 111471 |
| scikit-learn__scikit-learn-11040 | medium | no | completed | 6 | 5 | 48902 |
| scikit-learn__scikit-learn-14092 | medium | no | completed | 14 | 13 | 98212 |
| pytest-dev__pytest-6116 | medium | yes | completed | 8 | 7 | 46230 |
| scikit-learn__scikit-learn-10508 | medium | yes | completed | 5 | 4 | 27711 |
| sphinx-doc__sphinx-7686 | medium | yes | completed | 4 | 3 | 25403 |
| astropy__astropy-6938 | medium | yes | completed | 11 | 10 | 66831 |
| scikit-learn__scikit-learn-10949 | medium | yes | completed | 13 | 12 | 76796 |
| scikit-learn__scikit-learn-10297 | medium | yes | completed | 6 | 5 | 41439 |
| pytest-dev__pytest-5221 | medium | yes | completed | 13 | 12 | 73702 |
| pytest-dev__pytest-7373 | medium | yes | completed | 8 | 7 | 44469 |
| sphinx-doc__sphinx-8282 | medium | yes | completed | 12 | 11 | 86268 |
| pytest-dev__pytest-7432 | medium | yes | completed | 11 | 10 | 56780 |
| sphinx-doc__sphinx-8435 | medium | yes | completed | 14 | 13 | 84802 |
| sphinx-doc__sphinx-8273 | medium | yes | completed | 12 | 11 | 67352 |
| django__django-14238 | large | yes | completed | 8 | 6 | 43950 |
| django__django-12915 | large | yes | completed | 6 | 5 | 28826 |
| matplotlib__matplotlib-25442 | large | yes | completed | 6 | 5 | 59130 |
| sympy__sympy-17630 | large | no | error | 0 | 0 | 22960 |
| django__django-11099 | large | yes | completed | 8 | 7 | 35067 |
| sympy__sympy-23117 | large | no | completed | 8 | 7 | 81251 |
| django__django-14730 | large | no | completed | 16 | 15 | 149170 |
| django__django-14752 | large | yes | completed | 14 | 13 | 73147 |
| sympy__sympy-16503 | large | no | failed | 18 | 15 | 152065 |
| django__django-10914 | large | no | failed | 18 | 15 | 106990 |
| sympy__sympy-13895 | large | no | completed | 18 | 17 | 269252 |
| django__django-13768 | large | yes | completed | 16 | 15 | 69894 |
| django__django-11001 | large | no | completed | 5 | 4 | 22551 |
| sympy__sympy-12454 | large | yes | completed | 8 | 7 | 55822 |
| sympy__sympy-20154 | large | yes | completed | 14 | 13 | 113375 |

## Errors

- `sympy__sympy-17630`: RuntimeError: Model request failed after retries: Model returned an empty message.

## Task families

| Family | Passed | Total | Pass rate |
|---|---:|---:|---:|
| large | 8 | 15 | 53.3% |
| medium | 13 | 15 | 86.7% |
| small | 8 | 14 | 57.1% |

## Interpretation

Results depend on the selected model, endpoint, prompt version, and case set. Do not compare reports unless these inputs are held constant.
