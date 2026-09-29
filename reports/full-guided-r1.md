# RepoAgent Benchmark Report

> Generated from executable JSONL cases. A passing case requires Agent completion and all deterministic assertions; a localization case passes when its top-ranked location names a gold function.

## Summary

- Model: deepseek-flash
- Provider model: deepseek-flash
- AST tools: enabled
- Context retrieval: enabled
- AST guidance prompt: on
- Cases: 44
- Passed: 32
- Pass rate: 72.7%
- Average steps: 9.68
- Average tool calls: 8.57
- Tool errors: 10
- Model errors: 3
- Provider request attempts: 562
- JSON repair retries: 40
- Locally closed brackets: 19
- AST tool calls: 91
- Total tokens: 2940644

### Localization (n=41)

- function_recall@1: 61.5%
- function_recall@3: 73.6%
- function_recall@5: 74.6%
- file_acc@1: 92.7%
- file_acc@3: 95.1%
- file_acc@5: 95.1%

## Cases

| Case | Family | Passed | Status | Steps | Tool calls | Tokens |
|---|---|---:|---|---:|---:|---:|
| pydata__xarray-4248 | small | no | completed | 7 | 6 | 55713 |
| pallets__flask-5063 | small | yes | completed | 8 | 7 | 59114 |
| psf__requests-2148 | small | yes | completed | 7 | 6 | 57178 |
| mwaskom__seaborn-3010 | small | no | completed | 5 | 4 | 29567 |
| psf__requests-2674 | small | yes | completed | 15 | 14 | 93631 |
| pallets__flask-4992 | small | yes | completed | 8 | 7 | 33341 |
| mwaskom__seaborn-2848 | small | no | completed | 16 | 15 | 98626 |
| pallets__flask-4045 | small | yes | completed | 16 | 15 | 125101 |
| psf__requests-863 | small | yes | completed | 14 | 13 | 72936 |
| psf__requests-2317 | small | yes | completed | 14 | 13 | 87862 |
| psf__requests-3362 | small | no | completed | 10 | 8 | 58667 |
| pydata__xarray-3364 | small | no | error | 0 | 0 | 2688 |
| pydata__xarray-4094 | small | yes | completed | 5 | 4 | 25137 |
| psf__requests-1963 | small | yes | completed | 11 | 9 | 48353 |
| scikit-learn__scikit-learn-15535 | medium | yes | completed | 8 | 7 | 62846 |
| scikit-learn__scikit-learn-11040 | medium | no | completed | 12 | 11 | 106520 |
| scikit-learn__scikit-learn-14092 | medium | yes | completed | 9 | 8 | 57385 |
| pytest-dev__pytest-6116 | medium | yes | completed | 13 | 12 | 98969 |
| scikit-learn__scikit-learn-10508 | medium | yes | completed | 4 | 3 | 12791 |
| sphinx-doc__sphinx-7686 | medium | yes | completed | 8 | 7 | 65546 |
| astropy__astropy-6938 | medium | yes | completed | 8 | 6 | 58984 |
| scikit-learn__scikit-learn-10949 | medium | yes | completed | 8 | 7 | 58832 |
| scikit-learn__scikit-learn-10297 | medium | yes | completed | 6 | 5 | 39875 |
| pytest-dev__pytest-5221 | medium | no | error | 0 | 0 | 2224 |
| pytest-dev__pytest-7373 | medium | yes | completed | 8 | 7 | 45617 |
| sphinx-doc__sphinx-8282 | medium | yes | completed | 9 | 8 | 69576 |
| pytest-dev__pytest-7432 | medium | yes | completed | 3 | 2 | 14982 |
| sphinx-doc__sphinx-8435 | medium | yes | completed | 17 | 16 | 144787 |
| sphinx-doc__sphinx-8273 | medium | yes | completed | 15 | 14 | 84574 |
| django__django-14238 | large | yes | completed | 7 | 6 | 36163 |
| django__django-12915 | large | yes | completed | 17 | 16 | 85981 |
| matplotlib__matplotlib-25442 | large | no | completed | 16 | 15 | 135294 |
| sympy__sympy-17630 | large | no | error | 0 | 0 | 14911 |
| django__django-11099 | large | no | completed | 7 | 6 | 25780 |
| sympy__sympy-23117 | large | yes | completed | 16 | 14 | 131513 |
| django__django-14730 | large | no | completed | 17 | 16 | 135450 |
| django__django-14752 | large | yes | completed | 5 | 4 | 22283 |
| sympy__sympy-16503 | large | yes | completed | 7 | 6 | 41352 |
| django__django-10914 | large | yes | completed | 16 | 14 | 91087 |
| sympy__sympy-13895 | large | no | failed | 18 | 16 | 199468 |
| django__django-13768 | large | yes | completed | 6 | 5 | 21937 |
| django__django-11001 | large | yes | completed | 16 | 15 | 117595 |
| sympy__sympy-12454 | large | yes | completed | 6 | 5 | 26124 |
| sympy__sympy-20154 | large | yes | completed | 8 | 5 | 84284 |

## Errors

- `pydata__xarray-3364`: RuntimeError: Model request failed after retries: Model response did not contain a JSON object.
- `pytest-dev__pytest-5221`: RuntimeError: Model request failed after retries: Model response did not contain a JSON object.
- `sympy__sympy-17630`: RuntimeError: Model request failed after retries: Model response did not contain a JSON object.

## Task families

| Family | Passed | Total | Pass rate |
|---|---:|---:|---:|
| large | 10 | 15 | 66.7% |
| medium | 13 | 15 | 86.7% |
| small | 9 | 14 | 64.3% |

## Interpretation

Results depend on the selected model, endpoint, prompt version, and case set. Do not compare reports unless these inputs are held constant.
