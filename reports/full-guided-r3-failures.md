# Failure breakdown: full-guided-r3.json

Model: deepseek-flash · cases: 44 · pass 29 · wrong_symbol 8 · step_budget 3 · ranking 2 · protocol 1 · wrong_file 1

| Case | Tier | Label | Steps | First gold touch | AST calls | Tokens | Top-1 | Gold |
|---|---|---|---:|---:|---:|---:|---|---|
| pydata__xarray-4248 | small | step_budget | 18 | 1 | 2 | 104744 | `` | `xarray/core/formatting.py::inline_variable_array_repr` |
| pallets__flask-5063 | small | pass | 12 | 1 | 1 | 44480 | `src/flask/cli.py::routes_command` | `src/flask/cli.py::routes_command` |
| psf__requests-2148 | small | wrong_symbol | 13 | 1 | 2 | 114207 | `requests/models.py::Response.iter_content` | `requests/models.py::Response.iter_content.generate` |
| mwaskom__seaborn-3010 | small | wrong_symbol | 7 | 1 | 2 | 36701 | `seaborn/_stats/regression.py::PolyFit._fit_predict` | `seaborn/_stats/regression.py::PolyFit.__call__` |
| psf__requests-2674 | small | pass | 14 | 1 | 4 | 137202 | `requests/adapters.py::HTTPAdapter.send` | `requests/adapters.py::HTTPAdapter.send` |
| pallets__flask-4992 | small | pass | 8 | 1 | 1 | 30266 | `src/flask/config.py::Config.from_file` | `src/flask/config.py::Config.from_file` |
| mwaskom__seaborn-2848 | small | pass | 16 | 4 | 4 | 169828 | `seaborn/_oldcore.py::HueMapping._lookup_single` | `seaborn/_oldcore.py::HueMapping._lookup_single` |
| pallets__flask-4045 | small | pass | 12 | 1 | 2 | 76062 | `src/flask/blueprints.py::Blueprint.__init__` | `src/flask/blueprints.py::Blueprint.__init__; src/flask/blueprints.py::Blueprint.add_url_rule` |
| psf__requests-863 | small | wrong_symbol | 13 | 1 | 2 | 102325 | `requests/models.py::Request.__init__` | `requests/models.py::Request.register_hook` |
| psf__requests-2317 | small | pass | 12 | 2 | 4 | 78375 | `requests/sessions.py::Session.request` | `requests/sessions.py::Session.request` |
| psf__requests-3362 | small | ranking | 12 | 4 | 3 | 70395 | `requests/models.py::Response.iter_content` | `requests/utils.py::stream_decode_response_unicode` |
| pydata__xarray-3364 | small | wrong_symbol | 13 | 1 | 2 | 108334 | `xarray/core/concat.py::concat` | `xarray/core/concat.py::_dataset_concat` |
| pydata__xarray-4094 | small | pass | 8 | 1 | 2 | 62400 | `xarray/core/dataarray.py::DataArray.to_unstacked_dataset` | `xarray/core/dataarray.py::DataArray.to_unstacked_dataset` |
| psf__requests-1963 | small | pass | 10 | 2 | 4 | 66491 | `requests/sessions.py::SessionRedirectMixin.resolve_redirects` | `requests/sessions.py::SessionRedirectMixin.resolve_redirects` |
| scikit-learn__scikit-learn-15535 | medium | pass | 13 | 1 | 4 | 111471 | `sklearn/metrics/cluster/_supervised.py::check_clusterings` | `sklearn/metrics/cluster/_supervised.py::check_clusterings` |
| scikit-learn__scikit-learn-11040 | medium | wrong_symbol | 6 | 1 | 3 | 48902 | `sklearn/neighbors/base.py::NeighborsBase._check_n_neighbors` | `sklearn/neighbors/base.py::NeighborsBase._fit; sklearn/neighbors/base.py::KNeighborsMixin.kneighbors` |
| scikit-learn__scikit-learn-14092 | medium | ranking | 14 | 1 | 4 | 98212 | `sklearn/utils/validation.py::check_scalar` | `sklearn/neighbors/nca.py::NeighborhoodComponentsAnalysis._validate_params` |
| pytest-dev__pytest-6116 | medium | pass | 8 | 1 | 1 | 46230 | `src/_pytest/main.py::pytest_addoption` | `src/_pytest/main.py::pytest_addoption` |
| scikit-learn__scikit-learn-10508 | medium | pass | 5 | 1 | 2 | 27711 | `sklearn/preprocessing/label.py::LabelEncoder.transform` | `sklearn/preprocessing/label.py::LabelEncoder.transform; sklearn/preprocessing/label.py::LabelEncoder.inverse_transform` |
| sphinx-doc__sphinx-7686 | medium | pass | 4 | 1 | 1 | 25403 | `sphinx/ext/autosummary/generate.py::generate_autosummary_content` | `sphinx/ext/autosummary/generate.py::generate_autosummary_content` |
| astropy__astropy-6938 | medium | pass | 11 | 1 | 2 | 66831 | `astropy/io/fits/fitsrec.py::FITS_rec._scale_back_ascii` | `astropy/io/fits/fitsrec.py::FITS_rec._scale_back_ascii` |
| scikit-learn__scikit-learn-10949 | medium | pass | 13 | 1 | 1 | 76796 | `sklearn/utils/validation.py::check_array` | `sklearn/utils/validation.py::check_array` |
| scikit-learn__scikit-learn-10297 | medium | pass | 6 | 1 | 2 | 41439 | `sklearn/linear_model/ridge.py::RidgeClassifierCV.__init__` | `sklearn/linear_model/ridge.py::RidgeCV; sklearn/linear_model/ridge.py::RidgeClassifierCV; sklearn/linear_model/ridge.py::RidgeClassifierCV.__init__` |
| pytest-dev__pytest-5221 | medium | pass | 13 | 1 | 3 | 73702 | `src/_pytest/python.py::_showfixtures_main` | `src/_pytest/python.py::_showfixtures_main` |
| pytest-dev__pytest-7373 | medium | pass | 8 | 1 | 2 | 44469 | `src/_pytest/mark/evaluate.py::MarkEvaluator._istrue` | `src/_pytest/mark/evaluate.py::cached_eval; src/_pytest/mark/evaluate.py::MarkEvaluator._istrue` |
| sphinx-doc__sphinx-8282 | medium | pass | 12 | 1 | 1 | 86268 | `sphinx/ext/autodoc/__init__.py::FunctionDocumenter.format_signature` | `sphinx/ext/autodoc/__init__.py::FunctionDocumenter.format_signature; sphinx/ext/autodoc/__init__.py::ClassDocumenter.format_signature; sphinx/ext/autodoc/__init__.py::MethodDocumenter.format_signature` |
| pytest-dev__pytest-7432 | medium | pass | 11 | 1 | 2 | 56780 | `src/_pytest/skipping.py::pytest_runtest_makereport` | `src/_pytest/skipping.py::pytest_runtest_makereport` |
| sphinx-doc__sphinx-8435 | medium | pass | 14 | 1 | 3 | 84802 | `sphinx/ext/autodoc/__init__.py::DataDocumenter.add_directive_header` | `sphinx/ext/autodoc/__init__.py::DataDocumenter.add_directive_header; sphinx/ext/autodoc/__init__.py::AttributeDocumenter.add_directive_header` |
| sphinx-doc__sphinx-8273 | medium | pass | 12 | 1 | 1 | 67352 | `sphinx/builders/manpage.py::ManualPageBuilder.write` | `sphinx/builders/manpage.py::ManualPageBuilder.write; sphinx/builders/manpage.py::setup` |
| django__django-14238 | large | pass | 8 | 2 | 1 | 43950 | `django/db/models/fields/__init__.py::AutoFieldMeta.__subclasscheck__` | `django/db/models/fields/__init__.py::AutoFieldMeta.__subclasscheck__` |
| django__django-12915 | large | pass | 6 | 1 | 1 | 28826 | `django/contrib/staticfiles/handlers.py::StaticFilesHandlerMixin.get_response` | `django/contrib/staticfiles/handlers.py` |
| matplotlib__matplotlib-25442 | large | pass | 6 | 1 | 2 | 59130 | `lib/matplotlib/offsetbox.py::DraggableBase.disconnect` | `lib/matplotlib/offsetbox.py::DraggableBase.__init__; lib/matplotlib/offsetbox.py::DraggableBase; lib/matplotlib/offsetbox.py::DraggableBase.on_pick; lib/matplotlib/offsetbox.py::DraggableBase.on_release; lib/matplotlib/offsetbox.py::DraggableBase.disconnect` |
| sympy__sympy-17630 | large | protocol | 0 | — | 0 | 22960 | `` | `sympy/matrices/expressions/matexpr.py::get_postprocessor._postprocessor` |
| django__django-11099 | large | pass | 8 | 1 | 3 | 35067 | `django/contrib/auth/validators.py::ASCIIUsernameValidator` | `django/contrib/auth/validators.py::ASCIIUsernameValidator; django/contrib/auth/validators.py::UnicodeUsernameValidator` |
| sympy__sympy-23117 | large | wrong_symbol | 8 | 1 | 3 | 81251 | `sympy/tensor/array/ndim_array.py::NDimArray._scan_iterable_shape` | `sympy/tensor/array/ndim_array.py::NDimArray._parse_index; sympy/tensor/array/ndim_array.py::NDimArray._scan_iterable_shape.f; sympy/tensor/array/ndim_array.py::NDimArray._check_index_for_getitem` |
| django__django-14730 | large | wrong_symbol | 16 | 1 | 4 | 149170 | `django/db/models/fields/related.py::ManyToManyField.check` | `django/db/models/fields/related.py::ManyToManyField._check_ignored_options` |
| django__django-14752 | large | pass | 14 | 1 | 2 | 73147 | `django/contrib/admin/views/autocomplete.py::AutocompleteJsonView.get` | `django/contrib/admin/views/autocomplete.py::AutocompleteJsonView.get; django/contrib/admin/views/autocomplete.py::AutocompleteJsonView` |
| sympy__sympy-16503 | large | step_budget | 18 | 1 | 2 | 152065 | `` | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Sum.asum; sympy/printing/pretty/pretty.py::PrettyPrinter._print_Sum` |
| django__django-10914 | large | step_budget | 18 | 1 | 1 | 106990 | `` | `django/conf/global_settings.py` |
| sympy__sympy-13895 | large | wrong_file | 18 | 11 | 4 | 269252 | `sympy/core/power.py::Pow.as_numer_denom` | `sympy/core/numbers.py::Integer._eval_power` |
| django__django-13768 | large | pass | 16 | 1 | 1 | 69894 | `django/dispatch/dispatcher.py::Signal.send_robust` | `django/dispatch/dispatcher.py::Signal.send_robust` |
| django__django-11001 | large | wrong_symbol | 5 | 1 | 1 | 22551 | `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` | `django/db/models/sql/compiler.py::SQLCompiler.__init__` |
| sympy__sympy-12454 | large | pass | 8 | 1 | 2 | 55822 | `sympy/matrices/matrices.py::MatrixProperties.is_upper` | `sympy/matrices/matrices.py::MatrixProperties._eval_is_upper_hessenberg; sympy/matrices/matrices.py::MatrixProperties.is_upper` |
| sympy__sympy-20154 | large | pass | 14 | 1 | 2 | 113375 | `sympy/utilities/iterables.py::partitions` | `sympy/utilities/iterables.py::partitions` |
