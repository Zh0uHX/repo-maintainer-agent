# Failure breakdown: baseline-real-10.json

Model: deepseek-flash · cases: 10 · pass 6 · wrong_symbol 3 · ranking 1

| Case | Tier | Label | Steps | First gold touch | AST calls | Tokens | Top-1 | Gold |
|---|---|---|---:|---:|---:|---:|---|---|
| pallets__flask-5063 | small | pass | 14 | 1 | 1 | 70447 | `src/flask/cli.py::routes_command` | `src/flask/cli.py::routes_command` |
| psf__requests-2148 | small | pass | 13 | 1 | 2 | 108056 | `requests/models.py::Response.iter_content.generate` | `requests/models.py::Response.iter_content.generate` |
| mwaskom__seaborn-3010 | small | wrong_symbol | 4 | 1 | 2 | 20016 | `seaborn/_stats/regression.py::PolyFit._fit_predict` | `seaborn/_stats/regression.py::PolyFit.__call__` |
| scikit-learn__scikit-learn-14092 | medium | pass | 16 | 1 | 3 | 98024 | `sklearn/neighbors/nca.py::NeighborhoodComponentsAnalysis._validate_params` | `sklearn/neighbors/nca.py::NeighborhoodComponentsAnalysis._validate_params` |
| pytest-dev__pytest-6116 | medium | pass | 11 | 1 | 0 | 48411 | `src/_pytest/main.py::pytest_addoption` | `src/_pytest/main.py::pytest_addoption` |
| django__django-14238 | large | wrong_symbol | 15 | 1 | 2 | 86762 | `django/db/models/fields/__init__.py::AutoFieldMeta` | `django/db/models/fields/__init__.py::AutoFieldMeta.__subclasscheck__` |
| matplotlib__matplotlib-25442 | large | pass | 11 | 1 | 1 | 78679 | `lib/matplotlib/offsetbox.py::DraggableBase.disconnect` | `lib/matplotlib/offsetbox.py::DraggableBase.__init__; lib/matplotlib/offsetbox.py::DraggableBase; lib/matplotlib/offsetbox.py::DraggableBase.on_pick; lib/matplotlib/offsetbox.py::DraggableBase.on_release; lib/matplotlib/offsetbox.py::DraggableBase.disconnect` |
| django__django-12915 | large | pass | 9 | 1 | 1 | 49617 | `django/contrib/staticfiles/handlers.py::StaticFilesHandlerMixin.get_response_async` | `django/contrib/staticfiles/handlers.py` |
| scikit-learn__scikit-learn-11040 | medium | wrong_symbol | 6 | 1 | 1 | 43374 | `sklearn/neighbors/base.py::NeighborsBase.__init__` | `sklearn/neighbors/base.py::NeighborsBase._fit; sklearn/neighbors/base.py::KNeighborsMixin.kneighbors` |
| sympy__sympy-17630 | large | ranking | 18 | 4 | 1 | 240673 | `sympy/matrices/expressions/blockmatrix.py::BlockMatrix._blockmul` | `sympy/matrices/expressions/matexpr.py::get_postprocessor._postprocessor` |
