# RepoAgent Ablation Comparison

- Machine-checkable comparison valid: yes
- Configured model match: yes
- Provider model match: yes
- Case count match: yes
- Exact case order match: yes
- Ablation dimension: ast
- Baseline AST: False
- Candidate AST: True
- Baseline context retrieval: False
- Candidate context retrieval: False
- Cases: 4 → 4

## Aggregate results

| Metric | String baseline | AST candidate | Observed change |
|---|---:|---:|---:|
| Pass rate | 100.0% | 100.0% | +0.0 pp |
| Average steps | 9.50 | 8.50 | -1.00 (-10.5%) |
| Average tool calls | 8.50 | 7.50 | -1.00 (-11.8%) |
| Tool errors | 0 | 0 | +0 |
| AST tool calls | 0 | 6 | +6 |
| Context retrieval calls | 0 | 0 | +0 |
| Total tokens | 65,662 | 57,412 | -8,250 (-12.6%) |

## Task families

| Family | Baseline | Candidate | Delta |
|---|---:|---:|---:|
| symbol-navigation | 100.0% | 100.0% | +0.0% |

## Per-case results

| Case | Passed | Steps | Tool calls | Tokens |
|---|---:|---:|---:|---:|
| locate-invoice-total-method | yes → yes | 9 → 9 | 8 → 8 | 13,981 → 13,280 |
| locate-user-repository-lookup | yes → yes | 6 → 6 | 5 → 5 | 7,271 → 8,381 |
| rename-token-store-method | yes → yes | 16 → 13 | 15 → 12 | 32,507 → 25,335 |
| locate-cache-falsey-value-bug | yes → yes | 7 → 6 | 6 → 5 | 11,903 → 10,416 |

> Treat the comparison as causal only when model, case set, prompts, step budget, and repeated-run protocol are held constant.
