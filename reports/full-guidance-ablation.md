# AST-guided prompt vs default prompt: 44 cases × 3 runs each

## Summary (facts only; interpretation is the author's call)

- Setup: deepseek-flash, SWE-bench Lite localization suite (44 cases, 14 small / 15 medium / 15 large),
  3 runs per condition, conditions interleaved at most 3 in parallel. Code `9d75e3c`; the 19 case-runs
  lost to a client crash were filled with `e65bbf1`, which only adds retries for dropped connections.
  9 of 264 case-runs ended in protocol errors (7 no JSON object, 2 empty replies) and count as failures.
- Headline metric, function recall@1 (42 cases with gold functions): default 0.481
  (95% CI 0.362–0.600), guided 0.568 (0.457–0.675). Paired difference +8.7 pp (CI +2.1 to +15.8).
- Cost side: guided used 1.7 fewer steps and 11.5k fewer tokens per case (−13%); both CIs exclude zero.
- Tier breakdown is exploratory (small n, many comparisons): the recall gain is clearest on small repos
  (+16.7 pp), zero on medium, +10.1 pp on large with a CI that crosses zero. No size trend.
- Same-configuration variance is large: default function recall@1 ranged 41.3%–55.6% across its 3 runs.
  Single-run comparisons on this suite are not reliable.
- The interim analysis (`full-guidance-interim.md`, 12 error-free cases, no large repos) reported no
  detectable gain. That subset was biased; this report supersedes it.
- Protocol recovery was routine, not rare: 283 JSON-mode fallbacks, 277 JSON repair rounds,
  103 locally closed brackets and 14 plan repairs across 264 case-runs.
- Spend for this rerun: 15.54 CNY for about 21.1M tokens (≈0.74 CNY per million).

## Generated tables

## Runs

| Condition | Run | Cases | Errors | Pass | fn recall@1 | Tokens |
|---|---|---:|---:|---:|---:|---:|
| default | full-default-r1 | 44 | 1 | 28 | 47.3% | 3,601,450 |
| default | full-default-r2 | 44 | 2 | 31 | 55.6% | 3,564,770 |
| default | full-default-r3 | 44 | 1 | 24 | 41.3% | 4,137,129 |
| default | recoveries | | | | | closed brackets 53, JSON repairs 157 |
| guided | full-guided-r1 | 44 | 3 | 32 | 57.1% | 2,940,644 |
| guided | full-guided-r2 | 44 | 1 | 34 | 61.1% | 3,402,260 |
| guided | full-guided-r3 | 44 | 1 | 29 | 52.1% | 3,441,628 |
| guided | recoveries | | | | | closed brackets 50, JSON repairs 120 |

## Per-condition means over 44 shared cases

| Metric | default | guided | Run range (default / guided) |
|---|---:|---:|---|
| pass | 62.9% | 72.0% | 54.5%–70.5% / 65.9%–77.3% |
| function_recall@1 | 48.1% | 56.8% | 41.3%–55.6% / 52.1%–61.1% |
| function_recall@5 | 63.4% | 72.2% | 61.3%–67.7% / 69.3%–75.2% |
| file_acc@1 | 82.6% | 86.4% | 77.3%–88.6% / 84.1%–88.6% |
| steps | 12.19 | 10.50 | 12.07–12.34 / 9.68–10.93 |
| tool_calls | 11.01 | 9.35 | 10.82–11.11 / 8.57–9.75 |
| ast_calls | 1.46 | 2.23 | 1.36–1.61 / 2.07–2.43 |
| tokens | 85,631 | 74,125 | 81,018–94,026 / 66,833–78,219 |

## Paired difference: guided − default (bootstrap over cases, 95% CI)

| Metric | all (n=44) | small (n=14) | medium (n=15) | large (n=15) |
|---|---|---|---|---|
| pass | +9.1 pp [-0.0 pp, +18.2 pp] | +16.7 pp [+4.8 pp, +31.0 pp] | +2.2 pp [-8.9 pp, +15.6 pp] | +8.9 pp [-11.1 pp, +26.7 pp] |
| function_recall@1 | +8.7 pp [+2.1 pp, +15.8 pp] | +16.7 pp [+4.8 pp, +31.0 pp] | -0.0 pp [-8.9 pp, +8.9 pp] | +10.1 pp [-0.6 pp, +23.2 pp] |
| function_recall@5 | +8.8 pp [+1.5 pp, +16.5 pp] | +11.9 pp [+0.0 pp, +23.8 pp] | +2.6 pp [-8.1 pp, +13.7 pp] | +12.6 pp [-1.2 pp, +28.7 pp] |
| file_acc@1 | +3.8 pp [-2.3 pp, +10.6 pp] | +11.9 pp [+4.8 pp, +21.4 pp] | +4.4 pp [-6.7 pp, +17.8 pp] | -4.4 pp [-15.6 pp, +6.7 pp] |
| steps | -1.69 [-2.45, -0.92] | -1.62 [-2.71, -0.55] | -1.96 [-3.47, -0.42] | -1.49 [-2.91, -0.18] |
| tool_calls | -1.66 [-2.41, -0.90] | -1.48 [-2.38, -0.55] | -1.84 [-3.38, -0.27] | -1.64 [-2.98, -0.36] |
| ast_calls | +0.77 [+0.53, +1.00] | +0.83 [+0.38, +1.31] | +0.84 [+0.64, +1.07] | +0.62 [+0.11, +1.13] |
| tokens | -11,506 [-18,669, -4,715] | -10,623 [-23,544, +498] | -13,783 [-24,795, -2,605] | -10,054 [-23,862, +1,808] |

An interval that excludes zero indicates a difference larger than case-to-case variation in this suite; it does not generalize beyond these cases, this model, or this prompt version.
