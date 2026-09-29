# RepoAgent Benchmark Report

> Generated from executable JSONL cases. A passing case requires Agent completion and all deterministic assertions; a localization case passes when its top-ranked location names a gold function.

## Summary

- Model: deepseek-flash
- Provider model: deepseek-flash
- AST tools: enabled
- Context retrieval: enabled
- AST guidance prompt: off
- Cases: 44
- Passed: 28
- Pass rate: 63.6%
- Average steps: 12.07
- Average tool calls: 10.82
- Tool errors: 16
- Model errors: 1
- Provider request attempts: 671
- JSON repair retries: 51
- Locally closed brackets: 18
- AST tool calls: 71
- Total tokens: 3601450

### Localization (n=43)

- function_recall@1: 48.5%
- function_recall@3: 62.3%
- function_recall@5: 62.8%
- file_acc@1: 83.7%
- file_acc@3: 88.4%
- file_acc@5: 88.4%

## Cases

| Case | Family | Passed | Status | Steps | Tool calls | Tokens |
|---|---|---:|---|---:|---:|---:|
| pydata__xarray-4248 | small | no | completed | 9 | 8 | 65830 |
| pallets__flask-5063 | small | yes | completed | 14 | 13 | 71662 |
| psf__requests-2148 | small | no | completed | 16 | 15 | 140785 |
| mwaskom__seaborn-3010 | small | no | completed | 4 | 3 | 23427 |
| psf__requests-2674 | small | no | failed | 18 | 15 | 127841 |
| pallets__flask-4992 | small | yes | completed | 6 | 5 | 25854 |
| mwaskom__seaborn-2848 | small | no | completed | 16 | 15 | 163262 |
| pallets__flask-4045 | small | yes | completed | 16 | 15 | 97356 |
| psf__requests-863 | small | no | completed | 14 | 13 | 83483 |
| psf__requests-2317 | small | yes | completed | 16 | 15 | 75975 |
| psf__requests-3362 | small | no | completed | 16 | 15 | 65708 |
| pydata__xarray-3364 | small | no | failed | 16 | 12 | 116215 |
| pydata__xarray-4094 | small | yes | completed | 8 | 7 | 61719 |
| psf__requests-1963 | small | yes | completed | 6 | 4 | 32169 |
| scikit-learn__scikit-learn-15535 | medium | yes | completed | 15 | 14 | 110357 |
| scikit-learn__scikit-learn-11040 | medium | yes | completed | 16 | 15 | 146124 |
| scikit-learn__scikit-learn-14092 | medium | no | failed | 18 | 15 | 110917 |
| pytest-dev__pytest-6116 | medium | yes | completed | 9 | 8 | 37034 |
| scikit-learn__scikit-learn-10508 | medium | yes | completed | 3 | 2 | 17249 |
| sphinx-doc__sphinx-7686 | medium | yes | completed | 13 | 12 | 82147 |
| astropy__astropy-6938 | medium | yes | completed | 16 | 15 | 81645 |
| scikit-learn__scikit-learn-10949 | medium | yes | completed | 4 | 3 | 27176 |
| scikit-learn__scikit-learn-10297 | medium | yes | completed | 5 | 4 | 30665 |
| pytest-dev__pytest-5221 | medium | yes | completed | 15 | 14 | 111037 |
| pytest-dev__pytest-7373 | medium | yes | completed | 14 | 13 | 80806 |
| sphinx-doc__sphinx-8282 | medium | yes | completed | 16 | 15 | 122986 |
| pytest-dev__pytest-7432 | medium | yes | completed | 7 | 6 | 46833 |
| sphinx-doc__sphinx-8435 | medium | yes | completed | 16 | 14 | 150607 |
| sphinx-doc__sphinx-8273 | medium | yes | completed | 14 | 13 | 77351 |
| django__django-14238 | large | no | completed | 14 | 13 | 72266 |
| django__django-12915 | large | yes | completed | 13 | 12 | 70059 |
| matplotlib__matplotlib-25442 | large | yes | completed | 13 | 12 | 109172 |
| sympy__sympy-17630 | large | no | completed | 5 | 4 | 52341 |
| django__django-11099 | large | no | completed | 4 | 3 | 7830 |
| sympy__sympy-23117 | large | no | completed | 12 | 11 | 99488 |
| django__django-14730 | large | no | completed | 18 | 15 | 132327 |
| django__django-14752 | large | no | error | 0 | 0 | 5167 |
| sympy__sympy-16503 | large | yes | completed | 16 | 15 | 99711 |
| django__django-10914 | large | yes | completed | 16 | 15 | 99684 |
| sympy__sympy-13895 | large | no | completed | 15 | 14 | 163295 |
| django__django-13768 | large | yes | completed | 7 | 6 | 28514 |
| django__django-11001 | large | yes | completed | 14 | 12 | 92895 |
| sympy__sympy-12454 | large | yes | completed | 13 | 12 | 64231 |
| sympy__sympy-20154 | large | yes | completed | 15 | 14 | 120250 |

## Errors

- `django__django-14752`: RuntimeError: Model request failed after retries: Model response did not contain a JSON object.

## Task families

| Family | Passed | Total | Pass rate |
|---|---:|---:|---:|
| large | 8 | 15 | 53.3% |
| medium | 14 | 15 | 93.3% |
| small | 6 | 14 | 42.9% |

## Interpretation

Results depend on the selected model, endpoint, prompt version, and case set. Do not compare reports unless these inputs are held constant.
