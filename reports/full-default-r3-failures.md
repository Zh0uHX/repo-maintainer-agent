# Failure breakdown: full-default-r3.json

Model: deepseek-flash · cases: 44 · pass 24 · wrong_symbol 10 · step_budget 3 · ranking 3 · wrong_file 2 · protocol 1 · tool_errors 1

| Case | Tier | Label | Steps | First gold touch | AST calls | Tokens | Top-1 | Gold |
|---|---|---|---:|---:|---:|---:|---|---|
| pydata__xarray-4248 | small | step_budget | 18 | 1 | 2 | 139213 | `` | `xarray/core/formatting.py::inline_variable_array_repr` |
| pallets__flask-5063 | small | pass | 9 | 1 | 2 | 56874 | `src/flask/cli.py::routes_command` | `src/flask/cli.py::routes_command` |
| psf__requests-2148 | small | wrong_symbol | 14 | 1 | 1 | 132932 | `requests/models.py::Response.iter_content` | `requests/models.py::Response.iter_content.generate` |
| mwaskom__seaborn-3010 | small | protocol | 0 | — | 0 | 6176 | `` | `seaborn/_stats/regression.py::PolyFit.__call__` |
| psf__requests-2674 | small | pass | 16 | 1 | 0 | 133684 | `requests/adapters.py::HTTPAdapter.send` | `requests/adapters.py::HTTPAdapter.send` |
| pallets__flask-4992 | small | pass | 8 | 1 | 1 | 34226 | `src/flask/config.py::Config.from_file` | `src/flask/config.py::Config.from_file` |
| mwaskom__seaborn-2848 | small | ranking | 18 | 1 | 3 | 151768 | `seaborn/axisgrid.py::PairGrid.__init__` | `seaborn/_oldcore.py::HueMapping._lookup_single` |
| pallets__flask-4045 | small | pass | 11 | 1 | 2 | 84140 | `src/flask/blueprints.py::Blueprint.__init__` | `src/flask/blueprints.py::Blueprint.__init__; src/flask/blueprints.py::Blueprint.add_url_rule` |
| psf__requests-863 | small | wrong_symbol | 15 | 1 | 2 | 98419 | `requests/models.py::Request.__init__` | `requests/models.py::Request.register_hook` |
| psf__requests-2317 | small | pass | 7 | 1 | 0 | 20224 | `requests/sessions.py::Session.request` | `requests/sessions.py::Session.request` |
| psf__requests-3362 | small | ranking | 7 | 1 | 1 | 66558 | `requests/models.py::Response.iter_content` | `requests/utils.py::stream_decode_response_unicode` |
| pydata__xarray-3364 | small | wrong_symbol | 13 | 1 | 1 | 112679 | `xarray/core/concat.py::concat` | `xarray/core/concat.py::_dataset_concat` |
| pydata__xarray-4094 | small | tool_errors | 18 | 1 | 3 | 181168 | `` | `xarray/core/dataarray.py::DataArray.to_unstacked_dataset` |
| psf__requests-1963 | small | pass | 16 | 1 | 2 | 68557 | `requests/sessions.py::SessionRedirectMixin.resolve_redirects` | `requests/sessions.py::SessionRedirectMixin.resolve_redirects` |
| scikit-learn__scikit-learn-15535 | medium | pass | 7 | 1 | 1 | 64112 | `sklearn/metrics/cluster/_supervised.py::check_clusterings` | `sklearn/metrics/cluster/_supervised.py::check_clusterings` |
| scikit-learn__scikit-learn-11040 | medium | wrong_symbol | 13 | 1 | 1 | 96056 | `sklearn/neighbors/base.py::NeighborsBase.fit` | `sklearn/neighbors/base.py::NeighborsBase._fit; sklearn/neighbors/base.py::KNeighborsMixin.kneighbors` |
| scikit-learn__scikit-learn-14092 | medium | ranking | 16 | 1 | 2 | 105689 | `sklearn/utils/validation.py::check_scalar` | `sklearn/neighbors/nca.py::NeighborhoodComponentsAnalysis._validate_params` |
| pytest-dev__pytest-6116 | medium | pass | 15 | 1 | 2 | 87553 | `src/_pytest/main.py::pytest_addoption` | `src/_pytest/main.py::pytest_addoption` |
| scikit-learn__scikit-learn-10508 | medium | pass | 7 | 1 | 1 | 49994 | `sklearn/preprocessing/label.py::LabelEncoder.transform` | `sklearn/preprocessing/label.py::LabelEncoder.transform; sklearn/preprocessing/label.py::LabelEncoder.inverse_transform` |
| sphinx-doc__sphinx-7686 | medium | pass | 8 | 1 | 1 | 65095 | `sphinx/ext/autosummary/generate.py::generate_autosummary_content` | `sphinx/ext/autosummary/generate.py::generate_autosummary_content` |
| astropy__astropy-6938 | medium | pass | 16 | 1 | 1 | 103041 | `astropy/io/fits/fitsrec.py::FITS_rec._scale_back_ascii` | `astropy/io/fits/fitsrec.py::FITS_rec._scale_back_ascii` |
| scikit-learn__scikit-learn-10949 | medium | pass | 7 | 1 | 0 | 58684 | `sklearn/utils/validation.py::check_array` | `sklearn/utils/validation.py::check_array` |
| scikit-learn__scikit-learn-10297 | medium | pass | 8 | 1 | 2 | 78454 | `sklearn/linear_model/ridge.py::RidgeClassifierCV.__init__` | `sklearn/linear_model/ridge.py::RidgeCV; sklearn/linear_model/ridge.py::RidgeClassifierCV; sklearn/linear_model/ridge.py::RidgeClassifierCV.__init__` |
| pytest-dev__pytest-5221 | medium | pass | 12 | 1 | 1 | 68111 | `src/_pytest/python.py::_showfixtures_main` | `src/_pytest/python.py::_showfixtures_main` |
| pytest-dev__pytest-7373 | medium | pass | 8 | 1 | 1 | 41018 | `src/_pytest/mark/evaluate.py::cached_eval` | `src/_pytest/mark/evaluate.py::cached_eval; src/_pytest/mark/evaluate.py::MarkEvaluator._istrue` |
| sphinx-doc__sphinx-8282 | medium | pass | 12 | 1 | 0 | 78678 | `sphinx/ext/autodoc/__init__.py::FunctionDocumenter.format_signature` | `sphinx/ext/autodoc/__init__.py::FunctionDocumenter.format_signature; sphinx/ext/autodoc/__init__.py::ClassDocumenter.format_signature; sphinx/ext/autodoc/__init__.py::MethodDocumenter.format_signature` |
| pytest-dev__pytest-7432 | medium | pass | 8 | 1 | 0 | 59485 | `src/_pytest/skipping.py::pytest_runtest_makereport` | `src/_pytest/skipping.py::pytest_runtest_makereport` |
| sphinx-doc__sphinx-8435 | medium | step_budget | 18 | 1 | 3 | 172239 | `` | `sphinx/ext/autodoc/__init__.py::DataDocumenter.add_directive_header; sphinx/ext/autodoc/__init__.py::AttributeDocumenter.add_directive_header` |
| sphinx-doc__sphinx-8273 | medium | step_budget | 18 | 1 | 1 | 112910 | `` | `sphinx/builders/manpage.py::ManualPageBuilder.write; sphinx/builders/manpage.py::setup` |
| django__django-14238 | large | wrong_symbol | 16 | 1 | 2 | 110742 | `django/db/models/fields/__init__.py::AutoFieldMeta._subclasses` | `django/db/models/fields/__init__.py::AutoFieldMeta.__subclasscheck__` |
| django__django-12915 | large | pass | 10 | 1 | 2 | 57369 | `django/contrib/staticfiles/handlers.py::StaticFilesHandlerMixin` | `django/contrib/staticfiles/handlers.py` |
| matplotlib__matplotlib-25442 | large | pass | 15 | 1 | 2 | 174095 | `lib/matplotlib/offsetbox.py::DraggableBase.__init__` | `lib/matplotlib/offsetbox.py::DraggableBase.__init__; lib/matplotlib/offsetbox.py::DraggableBase; lib/matplotlib/offsetbox.py::DraggableBase.on_pick; lib/matplotlib/offsetbox.py::DraggableBase.on_release; lib/matplotlib/offsetbox.py::DraggableBase.disconnect` |
| sympy__sympy-17630 | large | wrong_file | 16 | 4 | 2 | 235439 | `sympy/matrices/expressions/blockmatrix.py::BlockMatrix._blockmul` | `sympy/matrices/expressions/matexpr.py::get_postprocessor._postprocessor` |
| django__django-11099 | large | wrong_symbol | 8 | 1 | 1 | 23593 | `django/contrib/auth/validators.py::ASCIIUsernameValidator.regex` | `django/contrib/auth/validators.py::ASCIIUsernameValidator; django/contrib/auth/validators.py::UnicodeUsernameValidator` |
| sympy__sympy-23117 | large | wrong_symbol | 4 | 1 | 0 | 24543 | `sympy/tensor/array/ndim_array.py::NDimArray._scan_iterable_shape` | `sympy/tensor/array/ndim_array.py::NDimArray._parse_index; sympy/tensor/array/ndim_array.py::NDimArray._scan_iterable_shape.f; sympy/tensor/array/ndim_array.py::NDimArray._check_index_for_getitem` |
| django__django-14730 | large | wrong_symbol | 15 | 1 | 2 | 120620 | `django/db/models/fields/related.py::ManyToManyField._check_symmetrical_related_name` | `django/db/models/fields/related.py::ManyToManyField._check_ignored_options` |
| django__django-14752 | large | pass | 12 | 1 | 3 | 87314 | `django/contrib/admin/views/autocomplete.py::AutocompleteJsonView.get` | `django/contrib/admin/views/autocomplete.py::AutocompleteJsonView.get; django/contrib/admin/views/autocomplete.py::AutocompleteJsonView` |
| sympy__sympy-16503 | large | pass | 16 | 1 | 2 | 131438 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Sum` | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Sum.asum; sympy/printing/pretty/pretty.py::PrettyPrinter._print_Sum` |
| django__django-10914 | large | pass | 16 | 1 | 1 | 106060 | `django/conf/global_settings.py::FILE_UPLOAD_PERMISSIONS` | `django/conf/global_settings.py` |
| sympy__sympy-13895 | large | wrong_file | 17 | 5 | 2 | 206301 | `sympy/core/power.py::Pow.as_content_primitive` | `sympy/core/numbers.py::Integer._eval_power` |
| django__django-13768 | large | pass | 15 | 1 | 1 | 57842 | `django/dispatch/dispatcher.py::Signal.send_robust` | `django/dispatch/dispatcher.py::Signal.send_robust` |
| django__django-11001 | large | wrong_symbol | 13 | 1 | 3 | 89642 | `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` | `django/db/models/sql/compiler.py::SQLCompiler.__init__` |
| sympy__sympy-12454 | large | wrong_symbol | 13 | 2 | 1 | 61006 | `sympy/matrices/matrices.py::Matrix.is_upper` | `sympy/matrices/matrices.py::MatrixProperties._eval_is_upper_hessenberg; sympy/matrices/matrices.py::MatrixProperties.is_upper` |
| sympy__sympy-20154 | large | pass | 14 | 1 | 1 | 123388 | `sympy/utilities/iterables.py::partitions` | `sympy/utilities/iterables.py::partitions` |
