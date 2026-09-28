# Failure breakdown: guided-real-10.json

Model: deepseek-flash · cases: 10 · pass 7 · wrong_symbol 2 · wrong_file 1

| Case | Tier | Label | Steps | First gold touch | AST calls | Tokens | Top-1 | Gold |
|---|---|---|---:|---:|---:|---:|---|---|
| pallets__flask-5063 | small | pass | 8 | 1 | 2 | 55178 | `src/flask/cli.py::routes_command` | `src/flask/cli.py::routes_command` |
| psf__requests-2148 | small | wrong_symbol | 8 | 1 | 2 | 64195 | `requests/models.py::Response.iter_content` | `requests/models.py::Response.iter_content.generate` |
| mwaskom__seaborn-3010 | small | wrong_symbol | 5 | 1 | 2 | 24228 | `seaborn/_stats/regression.py::PolyFit._fit_predict` | `seaborn/_stats/regression.py::PolyFit.__call__` |
| scikit-learn__scikit-learn-11040 | medium | pass | 6 | 1 | 1 | 43355 | `sklearn/neighbors/base.py::KNeighborsMixin.kneighbors` | `sklearn/neighbors/base.py::NeighborsBase._fit; sklearn/neighbors/base.py::KNeighborsMixin.kneighbors` |
| scikit-learn__scikit-learn-14092 | medium | pass | 8 | 1 | 4 | 60454 | `sklearn/neighbors/nca.py::NeighborhoodComponentsAnalysis._validate_params` | `sklearn/neighbors/nca.py::NeighborhoodComponentsAnalysis._validate_params` |
| pytest-dev__pytest-6116 | medium | pass | 11 | 1 | 1 | 76229 | `src/_pytest/main.py::pytest_addoption` | `src/_pytest/main.py::pytest_addoption` |
| django__django-14238 | large | pass | 12 | 1 | 3 | 80399 | `django/db/models/fields/__init__.py::AutoFieldMeta.__subclasscheck__` | `django/db/models/fields/__init__.py::AutoFieldMeta.__subclasscheck__` |
| django__django-12915 | large | pass | 12 | 1 | 2 | 51406 | `django/contrib/staticfiles/handlers.py::StaticFilesHandlerMixin.get_response` | `django/contrib/staticfiles/handlers.py` |
| matplotlib__matplotlib-25442 | large | pass | 12 | 1 | 3 | 106681 | `lib/matplotlib/offsetbox.py::DraggableBase.disconnect` | `lib/matplotlib/offsetbox.py::DraggableBase.__init__; lib/matplotlib/offsetbox.py::DraggableBase; lib/matplotlib/offsetbox.py::DraggableBase.on_pick; lib/matplotlib/offsetbox.py::DraggableBase.on_release; lib/matplotlib/offsetbox.py::DraggableBase.disconnect` |
| sympy__sympy-17630 | large | wrong_file | 12 | 4 | 1 | 120722 | `sympy/matrices/expressions/blockmatrix.py::BlockMatrix._blockmul` | `sympy/matrices/expressions/matexpr.py::get_postprocessor._postprocessor` |
