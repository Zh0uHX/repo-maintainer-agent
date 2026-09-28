# RepoAgent Ablation Comparison

- Machine-checkable comparison valid: yes
- Configured model match: yes
- Provider model match: yes
- Case count match: yes
- Exact case order match: yes
- Ablation dimension: ast_guidance
- Baseline AST: True
- Candidate AST: True
- Baseline context retrieval: True
- Candidate context retrieval: True
- Baseline AST guidance: False
- Candidate AST guidance: True
- Cases: 10 → 10

## Aggregate results

| Metric | Default prompt | AST-guided prompt | Observed change |
|---|---:|---:|---:|
| Pass rate | 60.0% | 70.0% | +10.0 pp |
| function_recall@1 | 46.7% | 52.2% | +5.5 pp |
| function_recall@5 | 71.1% | 68.9% | -2.2 pp |
| file_acc@1 | 90.0% | 90.0% | +0.0 pp |
| Average steps | 11.70 | 9.40 | -2.30 (-19.7%) |
| Average tool calls | 10.70 | 8.30 | -2.40 (-22.4%) |
| Tool errors | 0 | 1 | +1 |
| AST tool calls | 14 | 21 | +7 (+50.0%) |
| Context retrieval calls | 0 | 0 | +0 |
| Total tokens | 844,059 | 682,847 | -161,212 (-19.1%) |

## Task families

| Family | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| large | 50.0% | 75.0% | +25.0% |
| medium | 66.7% | 100.0% | +33.3% |
| small | 66.7% | 33.3% | -33.3% |

## Per-case results

| Case | Passed | Steps | Tool calls | Tokens |
|---|---:|---:|---:|---:|
| pallets__flask-5063 | yes → yes | 14 → 8 | 13 → 7 | 70,447 → 55,178 |
| psf__requests-2148 | yes → no | 13 → 8 | 12 → 7 | 108,056 → 64,195 |
| mwaskom__seaborn-3010 | no → no | 4 → 5 | 3 → 4 | 20,016 → 24,228 |
| scikit-learn__scikit-learn-11040 | no → yes | 6 → 6 | 5 → 5 | 43,374 → 43,355 |
| scikit-learn__scikit-learn-14092 | yes → yes | 16 → 8 | 15 → 7 | 98,024 → 60,454 |
| pytest-dev__pytest-6116 | yes → yes | 11 → 11 | 10 → 10 | 48,411 → 76,229 |
| django__django-14238 | no → yes | 15 → 12 | 14 → 11 | 86,762 → 80,399 |
| django__django-12915 | yes → yes | 9 → 12 | 8 → 10 | 49,617 → 51,406 |
| matplotlib__matplotlib-25442 | yes → yes | 11 → 12 | 10 → 11 | 78,679 → 106,681 |
| sympy__sympy-17630 | no → no | 18 → 12 | 17 → 11 | 240,673 → 120,722 |

> Treat the comparison as causal only when model, case set, prompts, step budget, and repeated-run protocol are held constant.
