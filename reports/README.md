# Curated Evaluation Evidence

This directory contains reproducible benchmark outputs. Public portfolio links should prefer the final reports below rather than transient retry artifacts.

| Report | Purpose |
|---|---|
| `pilot-ast.md` | Ten-case, five-family real-model pilot |
| `navigation-ast-final.md` | Final AST-enabled symbol-navigation probe |
| `navigation-string.md` | String-search baseline over the same four cases |
| `navigation-ablation.md` | Machine-checked AST versus string-search comparison |

The navigation comparison uses one run per condition over four synthetic cases. It demonstrates observed retrieval efficiency under that protocol, not general model superiority. Repeat each condition and expand the holdout before presenting confidence intervals or broad capability claims.

Directories matching `*-artifacts/` are local failure-analysis workspaces and are intentionally excluded from version control because they may contain generated repositories, caches and verbose traces.

The `context_retrieval.jsonl` suite is present in the repository, but context-retrieval reports are intentionally not listed as evidence until both disabled and enabled conditions have been executed with a non-revoked local API credential.
