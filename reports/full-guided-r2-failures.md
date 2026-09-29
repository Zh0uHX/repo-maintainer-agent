# Failure breakdown: full-guided-r2.json

Model: deepseek-flash · cases: 44 · pass 34 · wrong_symbol 5 · step_budget 3 · protocol 1 · wrong_file 1

| Case | Tier | Label | Steps | First gold touch | AST calls | Tokens | Top-1 | Gold |
|---|---|---|---:|---:|---:|---:|---|---|
| pydata__xarray-4248 | small | wrong_symbol | 7 | 1 | 2 | 72706 | `xarray/core/formatting.py::summarize_variable` | `xarray/core/formatting.py::inline_variable_array_repr` |
| pallets__flask-5063 | small | pass | 12 | 1 | 2 | 70658 | `src/flask/cli.py::routes_command` | `src/flask/cli.py::routes_command` |
| psf__requests-2148 | small | pass | 14 | 1 | 4 | 125094 | `requests/models.py::Response.iter_content.generate` | `requests/models.py::Response.iter_content.generate` |
| mwaskom__seaborn-3010 | small | wrong_symbol | 4 | 1 | 1 | 20394 | `seaborn/_stats/regression.py::PolyFit._fit_predict` | `seaborn/_stats/regression.py::PolyFit.__call__` |
| psf__requests-2674 | small | pass | 15 | 1 | 3 | 126296 | `requests/adapters.py::HTTPAdapter.send` | `requests/adapters.py::HTTPAdapter.send` |
| pallets__flask-4992 | small | pass | 8 | 1 | 3 | 41174 | `src/flask/config.py::Config.from_file` | `src/flask/config.py::Config.from_file` |
| mwaskom__seaborn-2848 | small | wrong_symbol | 16 | 4 | 4 | 143446 | `seaborn/_oldcore.py::HueMapping.__init__` | `seaborn/_oldcore.py::HueMapping._lookup_single` |
| pallets__flask-4045 | small | pass | 8 | 1 | 2 | 53687 | `src/flask/blueprints.py::Blueprint.__init__` | `src/flask/blueprints.py::Blueprint.__init__; src/flask/blueprints.py::Blueprint.add_url_rule` |
| psf__requests-863 | small | pass | 12 | 1 | 3 | 96749 | `requests/models.py::Request.register_hook` | `requests/models.py::Request.register_hook` |
| psf__requests-2317 | small | pass | 12 | 1 | 1 | 60616 | `requests/sessions.py::Session.request` | `requests/sessions.py::Session.request` |
| psf__requests-3362 | small | pass | 10 | 3 | 3 | 48390 | `requests/utils.py::stream_decode_response_unicode` | `requests/utils.py::stream_decode_response_unicode` |
| pydata__xarray-3364 | small | pass | 13 | 1 | 2 | 92930 | `xarray/core/concat.py::_dataset_concat` | `xarray/core/concat.py::_dataset_concat` |
| pydata__xarray-4094 | small | pass | 8 | 1 | 2 | 52125 | `xarray/core/dataarray.py::DataArray.to_unstacked_dataset` | `xarray/core/dataarray.py::DataArray.to_unstacked_dataset` |
| psf__requests-1963 | small | pass | 6 | 1 | 2 | 25840 | `requests/sessions.py::SessionRedirectMixin.resolve_redirects` | `requests/sessions.py::SessionRedirectMixin.resolve_redirects` |
| scikit-learn__scikit-learn-15535 | medium | pass | 8 | 2 | 3 | 84883 | `sklearn/metrics/cluster/_supervised.py::check_clusterings` | `sklearn/metrics/cluster/_supervised.py::check_clusterings` |
| scikit-learn__scikit-learn-11040 | medium | pass | 6 | 1 | 3 | 56063 | `sklearn/neighbors/base.py::NeighborsBase._fit` | `sklearn/neighbors/base.py::NeighborsBase._fit; sklearn/neighbors/base.py::KNeighborsMixin.kneighbors` |
| scikit-learn__scikit-learn-14092 | medium | pass | 16 | 1 | 5 | 98224 | `sklearn/neighbors/nca.py::NeighborhoodComponentsAnalysis._validate_params` | `sklearn/neighbors/nca.py::NeighborhoodComponentsAnalysis._validate_params` |
| pytest-dev__pytest-6116 | medium | pass | 16 | 1 | 3 | 104760 | `src/_pytest/main.py::pytest_addoption` | `src/_pytest/main.py::pytest_addoption` |
| scikit-learn__scikit-learn-10508 | medium | pass | 6 | 1 | 2 | 25027 | `sklearn/preprocessing/label.py::LabelEncoder.transform` | `sklearn/preprocessing/label.py::LabelEncoder.transform; sklearn/preprocessing/label.py::LabelEncoder.inverse_transform` |
| sphinx-doc__sphinx-7686 | medium | step_budget | 18 | 1 | 2 | 123317 | `` | `sphinx/ext/autosummary/generate.py::generate_autosummary_content` |
| astropy__astropy-6938 | medium | pass | 15 | 1 | 1 | 86782 | `astropy/io/fits/fitsrec.py::FITS_rec._scale_back_ascii` | `astropy/io/fits/fitsrec.py::FITS_rec._scale_back_ascii` |
| scikit-learn__scikit-learn-10949 | medium | pass | 8 | 1 | 2 | 64050 | `sklearn/utils/validation.py::check_array` | `sklearn/utils/validation.py::check_array` |
| scikit-learn__scikit-learn-10297 | medium | pass | 4 | 1 | 2 | 25189 | `sklearn/linear_model/ridge.py::RidgeClassifierCV.__init__` | `sklearn/linear_model/ridge.py::RidgeCV; sklearn/linear_model/ridge.py::RidgeClassifierCV; sklearn/linear_model/ridge.py::RidgeClassifierCV.__init__` |
| pytest-dev__pytest-5221 | medium | pass | 7 | 1 | 2 | 31986 | `src/_pytest/python.py::_showfixtures_main` | `src/_pytest/python.py::_showfixtures_main` |
| pytest-dev__pytest-7373 | medium | pass | 8 | 1 | 2 | 35220 | `src/_pytest/mark/evaluate.py::MarkEvaluator._istrue` | `src/_pytest/mark/evaluate.py::cached_eval; src/_pytest/mark/evaluate.py::MarkEvaluator._istrue` |
| sphinx-doc__sphinx-8282 | medium | pass | 12 | 1 | 2 | 108206 | `sphinx/ext/autodoc/__init__.py::FunctionDocumenter.format_signature` | `sphinx/ext/autodoc/__init__.py::FunctionDocumenter.format_signature; sphinx/ext/autodoc/__init__.py::ClassDocumenter.format_signature; sphinx/ext/autodoc/__init__.py::MethodDocumenter.format_signature` |
| pytest-dev__pytest-7432 | medium | pass | 7 | 1 | 1 | 35548 | `src/_pytest/skipping.py::pytest_runtest_makereport` | `src/_pytest/skipping.py::pytest_runtest_makereport` |
| sphinx-doc__sphinx-8435 | medium | pass | 16 | 1 | 3 | 145856 | `sphinx/ext/autodoc/__init__.py::DataDocumenter.add_directive_header` | `sphinx/ext/autodoc/__init__.py::DataDocumenter.add_directive_header; sphinx/ext/autodoc/__init__.py::AttributeDocumenter.add_directive_header` |
| sphinx-doc__sphinx-8273 | medium | pass | 13 | 1 | 2 | 63866 | `sphinx/builders/manpage.py::ManualPageBuilder.write` | `sphinx/builders/manpage.py::ManualPageBuilder.write; sphinx/builders/manpage.py::setup` |
| django__django-14238 | large | pass | 13 | 1 | 4 | 102624 | `django/db/models/fields/__init__.py::AutoFieldMeta.__subclasscheck__` | `django/db/models/fields/__init__.py::AutoFieldMeta.__subclasscheck__` |
| django__django-12915 | large | pass | 11 | 1 | 3 | 50077 | `django/contrib/staticfiles/handlers.py::StaticFilesHandlerMixin` | `django/contrib/staticfiles/handlers.py` |
| matplotlib__matplotlib-25442 | large | step_budget | 18 | 1 | 2 | 134985 | `` | `lib/matplotlib/offsetbox.py::DraggableBase.__init__; lib/matplotlib/offsetbox.py::DraggableBase; lib/matplotlib/offsetbox.py::DraggableBase.on_pick; lib/matplotlib/offsetbox.py::DraggableBase.on_release; lib/matplotlib/offsetbox.py::DraggableBase.disconnect` |
| sympy__sympy-17630 | large | protocol | 0 | — | 0 | 22883 | `` | `sympy/matrices/expressions/matexpr.py::get_postprocessor._postprocessor` |
| django__django-11099 | large | pass | 5 | 1 | 2 | 13142 | `django/contrib/auth/validators.py::ASCIIUsernameValidator` | `django/contrib/auth/validators.py::ASCIIUsernameValidator; django/contrib/auth/validators.py::UnicodeUsernameValidator` |
| sympy__sympy-23117 | large | wrong_symbol | 8 | 1 | 3 | 84769 | `sympy/tensor/array/ndim_array.py::NDimArray._scan_iterable_shape` | `sympy/tensor/array/ndim_array.py::NDimArray._parse_index; sympy/tensor/array/ndim_array.py::NDimArray._scan_iterable_shape.f; sympy/tensor/array/ndim_array.py::NDimArray._check_index_for_getitem` |
| django__django-14730 | large | step_budget | 18 | 1 | 3 | 133175 | `` | `django/db/models/fields/related.py::ManyToManyField._check_ignored_options` |
| django__django-14752 | large | pass | 11 | 1 | 2 | 61437 | `django/contrib/admin/views/autocomplete.py::AutocompleteJsonView.get` | `django/contrib/admin/views/autocomplete.py::AutocompleteJsonView.get; django/contrib/admin/views/autocomplete.py::AutocompleteJsonView` |
| sympy__sympy-16503 | large | pass | 15 | 1 | 4 | 148643 | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Sum` | `sympy/printing/pretty/pretty.py::PrettyPrinter._print_Sum.asum; sympy/printing/pretty/pretty.py::PrettyPrinter._print_Sum` |
| django__django-10914 | large | pass | 16 | 1 | 1 | 93054 | `django/conf/global_settings.py::FILE_UPLOAD_PERMISSIONS (module-level setting, line 307)` | `django/conf/global_settings.py` |
| sympy__sympy-13895 | large | wrong_file | 17 | — | 5 | 212379 | `sympy/simplify/powsimp.py::powsimp` | `sympy/core/numbers.py::Integer._eval_power` |
| django__django-13768 | large | pass | 6 | 1 | 2 | 27875 | `django/dispatch/dispatcher.py::Signal.send_robust` | `django/dispatch/dispatcher.py::Signal.send_robust` |
| django__django-11001 | large | wrong_symbol | 14 | 1 | 1 | 63994 | `django/db/models/sql/compiler.py::SQLCompiler.get_order_by` | `django/db/models/sql/compiler.py::SQLCompiler.__init__` |
| sympy__sympy-12454 | large | pass | 11 | 1 | 4 | 57418 | `sympy/matrices/matrices.py::MatrixProperties.is_upper` | `sympy/matrices/matrices.py::MatrixProperties._eval_is_upper_hessenberg; sympy/matrices/matrices.py::MatrixProperties.is_upper` |
| sympy__sympy-20154 | large | pass | 11 | 1 | 2 | 76723 | `sympy/utilities/iterables.py::partitions` | `sympy/utilities/iterables.py::partitions` |
