> **Superseded by `full-guidance-ablation.md`.** This interim cut used only the 12 cases that finished without error in all six interrupted runs (no large repositories) and its conclusion did not hold on the full data.

# Repeated-run localization comparison

## Runs

| Condition | Run | Cases | Errors | Pass | fn recall@1 | Tokens |
|---|---|---:|---:|---:|---:|---:|
| default | full-default-r1 | 44 | 19 | 18 | 33.3% | 1,759,756 |
| default | full-default-r2 | 44 | 21 | 16 | 29.9% | 1,852,267 |
| default | full-default-r3 | 44 | 22 | 19 | 36.7% | 1,710,023 |
| default | recoveries | | | | | closed brackets 26, JSON repairs 95 |
| guided | full-guided-r1 | 44 | 17 | 20 | 37.3% | 1,865,862 |
| guided | full-guided-r2 | 44 | 21 | 18 | 34.8% | 1,942,890 |
| guided | full-guided-r3 | 44 | 21 | 18 | 36.0% | 1,708,037 |
| guided | recoveries | | | | | closed brackets 26, JSON repairs 81 |

## Per-condition means over 12 cases without errors in any run (interim; excludes errored cases)

| Metric | default | guided | Run range (default / guided) |
|---|---:|---:|---|
| pass | 77.8% | 66.7% | 75.0%–83.3% / 58.3%–75.0% |
| function_recall@1 | 73.6% | 63.9% | 70.8%–79.2% / 58.3%–70.8% |
| function_recall@5 | 80.6% | 80.6% | 75.0%–83.3% / 75.0%–83.3% |
| file_acc@1 | 94.4% | 91.7% | 83.3%–100.0% / 83.3%–100.0% |
| steps | 11.39 | 10.97 | 10.75–11.83 / 10.42–11.25 |
| tool_calls | 10.06 | 9.92 | 9.58–10.83 / 9.25–10.25 |
| ast_calls | 1.36 | 1.89 | 1.17–1.58 / 1.75–2.00 |
| tokens | 73,840 | 76,183 | 64,745–80,107 / 71,533–84,902 |

## Paired difference: guided − default (bootstrap over cases, 95% CI)

| Metric | all (n=12) | small (n=8) | medium (n=4) | large (n=0) |
|---|---|---|---|---|
| pass | -11.1 pp [-33.3 pp, +11.1 pp] | -20.8 pp [-50.0 pp, +0.0 pp] | +8.3 pp [-25.0 pp, +50.0 pp] | — |
| function_recall@1 | -9.7 pp [-31.9 pp, +11.1 pp] | -20.8 pp [-50.0 pp, +0.0 pp] | +12.5 pp [-12.5 pp, +50.0 pp] | — |
| function_recall@5 | +0.0 pp [-11.1 pp, +13.9 pp] | -8.3 pp [-20.8 pp, +0.0 pp] | +16.7 pp [+0.0 pp, +50.0 pp] | — |
| file_acc@1 | -2.8 pp [-16.7 pp, +11.1 pp] | -8.3 pp [-29.2 pp, +8.3 pp] | +8.3 pp [+0.0 pp, +25.0 pp] | — |
| steps | -0.42 [-2.03, +1.28] | +0.58 [-1.42, +2.50] | -2.42 [-4.08, -0.50] | — |
| tool_calls | -0.14 [-1.50, +1.36] | +0.67 [-1.12, +2.50] | -1.75 [-2.83, -0.42] | — |
| ast_calls | +0.53 [+0.11, +0.92] | +0.75 [+0.33, +1.17] | +0.08 [-0.50, +0.67] | — |
| tokens | +2,343 [-15,532, +19,421] | +9,711 [-14,143, +29,329] | -12,393 [-33,305, +8,519] | — |

An interval that excludes zero indicates a difference larger than case-to-case variation in this suite; it does not generalize beyond these cases, this model, or this prompt version.
