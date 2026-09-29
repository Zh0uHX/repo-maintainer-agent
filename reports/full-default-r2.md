# RepoAgent Benchmark Report

> Generated from executable JSONL cases. A passing case requires Agent completion and all deterministic assertions; a localization case passes when its top-ranked location names a gold function.

## Summary

- Model: deepseek-flash
- Provider model: deepseek-flash
- AST tools: enabled
- Context retrieval: enabled
- AST guidance prompt: off
- Cases: 44
- Passed: 31
- Pass rate: 70.5%
- Average steps: 12.16
- Average tool calls: 11.11
- Tool errors: 9
- Model errors: 2
- Provider request attempts: 680
- JSON repair retries: 48
- Locally closed brackets: 17
- AST tool calls: 60
- Total tokens: 3564770

### Localization (n=42)

- function_recall@1: 58.4%
- function_recall@3: 71.1%
- function_recall@5: 71.1%
- file_acc@1: 92.9%
- file_acc@3: 95.2%
- file_acc@5: 95.2%

## Cases

| Case | Family | Passed | Status | Steps | Tool calls | Tokens |
|---|---|---:|---|---:|---:|---:|
| pydata__xarray-4248 | small | no | completed | 13 | 12 | 80860 |
| pallets__flask-5063 | small | yes | completed | 12 | 11 | 76919 |
| psf__requests-2148 | small | no | completed | 16 | 15 | 115114 |
| mwaskom__seaborn-3010 | small | no | completed | 5 | 4 | 25385 |
| psf__requests-2674 | small | yes | completed | 16 | 15 | 117150 |
| pallets__flask-4992 | small | yes | completed | 9 | 8 | 46382 |
| mwaskom__seaborn-2848 | small | yes | completed | 16 | 15 | 95342 |
| pallets__flask-4045 | small | yes | completed | 14 | 13 | 87676 |
| psf__requests-863 | small | no | completed | 10 | 9 | 59902 |
| psf__requests-2317 | small | yes | completed | 16 | 15 | 68401 |
| psf__requests-3362 | small | no | completed | 14 | 13 | 60365 |
| pydata__xarray-3364 | small | yes | completed | 13 | 12 | 120151 |
| pydata__xarray-4094 | small | yes | completed | 10 | 9 | 98408 |
| psf__requests-1963 | small | yes | completed | 8 | 7 | 36033 |
| scikit-learn__scikit-learn-15535 | medium | yes | completed | 11 | 10 | 74121 |
| scikit-learn__scikit-learn-11040 | medium | yes | completed | 14 | 13 | 126653 |
| scikit-learn__scikit-learn-14092 | medium | yes | completed | 13 | 12 | 98025 |
| pytest-dev__pytest-6116 | medium | yes | completed | 12 | 11 | 66019 |
| scikit-learn__scikit-learn-10508 | medium | yes | completed | 7 | 6 | 32770 |
| sphinx-doc__sphinx-7686 | medium | yes | completed | 10 | 9 | 89292 |
| astropy__astropy-6938 | medium | yes | completed | 16 | 15 | 85136 |
| scikit-learn__scikit-learn-10949 | medium | yes | completed | 5 | 4 | 27371 |
| scikit-learn__scikit-learn-10297 | medium | yes | completed | 12 | 11 | 78924 |
| pytest-dev__pytest-5221 | medium | yes | completed | 16 | 15 | 85303 |
| pytest-dev__pytest-7373 | medium | yes | completed | 16 | 15 | 86114 |
| sphinx-doc__sphinx-8282 | medium | yes | completed | 12 | 10 | 80534 |
| pytest-dev__pytest-7432 | medium | yes | completed | 12 | 11 | 82199 |
| sphinx-doc__sphinx-8435 | medium | yes | completed | 16 | 15 | 99304 |
| sphinx-doc__sphinx-8273 | medium | no | error | 0 | 0 | 3272 |
| django__django-14238 | large | yes | completed | 15 | 14 | 68278 |
| django__django-12915 | large | yes | completed | 15 | 14 | 110281 |
| matplotlib__matplotlib-25442 | large | yes | completed | 12 | 11 | 120071 |
| sympy__sympy-17630 | large | no | error | 0 | 0 | 14951 |
| django__django-11099 | large | no | completed | 6 | 5 | 16257 |
| sympy__sympy-23117 | large | no | failed | 18 | 15 | 128483 |
| django__django-14730 | large | no | completed | 16 | 15 | 126152 |
| django__django-14752 | large | yes | completed | 7 | 6 | 51873 |
| sympy__sympy-16503 | large | yes | completed | 16 | 14 | 101565 |
| django__django-10914 | large | yes | completed | 17 | 16 | 78097 |
| sympy__sympy-13895 | large | no | failed | 18 | 17 | 234253 |
| django__django-13768 | large | yes | completed | 16 | 15 | 78806 |
| django__django-11001 | large | no | completed | 11 | 10 | 43869 |
| sympy__sympy-12454 | large | no | completed | 8 | 7 | 46815 |
| sympy__sympy-20154 | large | yes | completed | 16 | 15 | 141894 |

## Errors

- `sphinx-doc__sphinx-8273`: RuntimeError: Model request failed after retries: Model response did not contain a JSON object.
- `sympy__sympy-17630`: RuntimeError: Model request failed after retries: Model response did not contain a JSON object.

## Task families

| Family | Passed | Total | Pass rate |
|---|---:|---:|---:|
| large | 8 | 15 | 53.3% |
| medium | 14 | 15 | 93.3% |
| small | 9 | 14 | 64.3% |

## Interpretation

Results depend on the selected model, endpoint, prompt version, and case set. Do not compare reports unless these inputs are held constant.
