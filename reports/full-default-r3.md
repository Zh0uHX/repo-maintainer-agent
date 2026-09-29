# RepoAgent Benchmark Report

> Generated from executable JSONL cases. A passing case requires Agent completion and all deterministic assertions; a localization case passes when its top-ranked location names a gold function.

## Summary

- Model: deepseek-flash
- Provider model: deepseek-flash
- AST tools: enabled
- Context retrieval: enabled
- AST guidance prompt: off
- Cases: 44
- Passed: 24
- Pass rate: 54.5%
- Average steps: 12.34
- Average tool calls: 11.09
- Tool errors: 18
- Model errors: 1
- Provider request attempts: 697
- JSON repair retries: 58
- Locally closed brackets: 18
- AST tool calls: 62
- Total tokens: 4137129

### Localization (n=43)

- function_recall@1: 42.4%
- function_recall@3: 60.7%
- function_recall@5: 62.8%
- file_acc@1: 79.1%
- file_acc@3: 86.1%
- file_acc@5: 86.1%

## Cases

| Case | Family | Passed | Status | Steps | Tool calls | Tokens |
|---|---|---:|---|---:|---:|---:|
| pydata__xarray-4248 | small | no | failed | 18 | 15 | 139213 |
| pallets__flask-5063 | small | yes | completed | 9 | 8 | 56874 |
| psf__requests-2148 | small | no | completed | 14 | 13 | 132932 |
| mwaskom__seaborn-3010 | small | no | error | 0 | 0 | 6176 |
| psf__requests-2674 | small | yes | completed | 16 | 14 | 133684 |
| pallets__flask-4992 | small | yes | completed | 8 | 7 | 34226 |
| mwaskom__seaborn-2848 | small | no | completed | 18 | 17 | 151768 |
| pallets__flask-4045 | small | yes | completed | 11 | 10 | 84140 |
| psf__requests-863 | small | no | completed | 15 | 14 | 98419 |
| psf__requests-2317 | small | yes | completed | 7 | 6 | 20224 |
| psf__requests-3362 | small | no | completed | 7 | 6 | 66558 |
| pydata__xarray-3364 | small | no | completed | 13 | 12 | 112679 |
| pydata__xarray-4094 | small | no | failed | 18 | 14 | 181168 |
| psf__requests-1963 | small | yes | completed | 16 | 15 | 68557 |
| scikit-learn__scikit-learn-15535 | medium | yes | completed | 7 | 6 | 64112 |
| scikit-learn__scikit-learn-11040 | medium | no | completed | 13 | 12 | 96056 |
| scikit-learn__scikit-learn-14092 | medium | no | completed | 16 | 15 | 105689 |
| pytest-dev__pytest-6116 | medium | yes | completed | 15 | 13 | 87553 |
| scikit-learn__scikit-learn-10508 | medium | yes | completed | 7 | 6 | 49994 |
| sphinx-doc__sphinx-7686 | medium | yes | completed | 8 | 7 | 65095 |
| astropy__astropy-6938 | medium | yes | completed | 16 | 15 | 103041 |
| scikit-learn__scikit-learn-10949 | medium | yes | completed | 7 | 6 | 58684 |
| scikit-learn__scikit-learn-10297 | medium | yes | completed | 8 | 7 | 78454 |
| pytest-dev__pytest-5221 | medium | yes | completed | 12 | 11 | 68111 |
| pytest-dev__pytest-7373 | medium | yes | completed | 8 | 7 | 41018 |
| sphinx-doc__sphinx-8282 | medium | yes | completed | 12 | 11 | 78678 |
| pytest-dev__pytest-7432 | medium | yes | completed | 8 | 7 | 59485 |
| sphinx-doc__sphinx-8435 | medium | no | failed | 18 | 15 | 172239 |
| sphinx-doc__sphinx-8273 | medium | no | failed | 18 | 14 | 112910 |
| django__django-14238 | large | no | completed | 16 | 15 | 110742 |
| django__django-12915 | large | yes | completed | 10 | 9 | 57369 |
| matplotlib__matplotlib-25442 | large | yes | completed | 15 | 14 | 174095 |
| sympy__sympy-17630 | large | no | completed | 16 | 15 | 235439 |
| django__django-11099 | large | no | completed | 8 | 7 | 23593 |
| sympy__sympy-23117 | large | no | completed | 4 | 3 | 24543 |
| django__django-14730 | large | no | completed | 15 | 14 | 120620 |
| django__django-14752 | large | yes | completed | 12 | 11 | 87314 |
| sympy__sympy-16503 | large | yes | completed | 16 | 15 | 131438 |
| django__django-10914 | large | yes | completed | 16 | 15 | 106060 |
| sympy__sympy-13895 | large | no | completed | 17 | 16 | 206301 |
| django__django-13768 | large | yes | completed | 15 | 14 | 57842 |
| django__django-11001 | large | no | completed | 13 | 12 | 89642 |
| sympy__sympy-12454 | large | no | completed | 13 | 12 | 61006 |
| sympy__sympy-20154 | large | yes | completed | 14 | 13 | 123388 |

## Errors

- `mwaskom__seaborn-3010`: RuntimeError: Model request failed after retries: Model response did not contain a JSON object.

## Task families

| Family | Passed | Total | Pass rate |
|---|---:|---:|---:|
| large | 7 | 15 | 46.7% |
| medium | 11 | 15 | 73.3% |
| small | 6 | 14 | 42.9% |

## Interpretation

Results depend on the selected model, endpoint, prompt version, and case set. Do not compare reports unless these inputs are held constant.
