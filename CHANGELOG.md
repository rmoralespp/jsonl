## Releases

- **Changed:** Documentation - Add UTF-8 headers to the Python code snippets shown.
- **Changed:** Enable more `ruff` rules and pass all checks.
- **Changed:** Docstrings - Enable all `sphinx-linter` rules and pass all checks.
- **Fixed:** Tests - Delay the closing of the `http_server` fixture socket to ensure that the thread closes properly.

### v1.3.21 (2025-11-04)

- **Changed:** **CI/CD** pipelines to apply (`sphinx-linter`, `pymport`) linters.
- **Changed:** `README.md` to include badges for GitHub Tag, GitHub Alerts and others for better visibility.
- **Changed:** `pyproject.toml` to include new linters (`sphinx-linter`, `pymport`).

### v1.3.20 (2025-10-22)

- **Added:** Added: Support por Python 3.14.
- **Changed:** Update Publish to PyPI GitHub Action in the CD pipeline.

### v1.3.19 (2025-09-16)

- **Changed:** The `load_archive` and `load` functions use number detection as a fallback when the file extension is not recognized.
- **Changed**: Documentation, indicate that **No external dependencies** are required.

### v1.3.18 (2025-09-15)

- **Changed**: Replace the deprecated `urllib.request.urlretrieve` because it is legacy.

### v1.3.17 (2025-09-12)

- **Added:** The `load_archive` function now supports loading data directly from a URL.
- **Added:** Acceptance tests to check the functionality of `load_archive` and `load` with URLs from a local HTTP server.
- **Changed:** The `load` function now use internally `urllib.request.urlretrieve` to download the file from a URL to a temporary file before loading it.
- **Changed**: Documentation, show that the NDJSON specification is supported
- **Fixed**: Documentation, a note from `dump_archive.md` referencing a param with an incorrect name.

### v1.3.16 (2025-07-23)

- **Added:** The `load` function now supports loading data directly from a URL.
- **Added:** `dump_archive` and `dump_fork` now accept `pathlib.Path` objects as valid file path inputs.

### v1.3.15 (2025-07-07)

- **Improved:** Documentation for better user guidance.

### v1.3.14 (2025-07-07)

- **Added**: `dump_archive` function to dump JSON Lines files into an archive (zip or tar)
- **Changed**: Update documentation site during **CD** pipeline instead of CI pipeline
- **Changed**: Add Ruff linter integration to **CI** pipeline

### v1.3.13 (2025-06-25)

- **Added**: `load_archive` function to load JSON Lines files from an archive (zip or tar)
- **Changed**: Coverage is now 100%.
- **Changed**: Improved docstrings.
- **Changed**: Only the functions `dump`, `dumper`, `dumps`, `dump_fork`, `load`, `loader`, and `load_archive` are now
  public. Everything else is considered internal and private, intended solely for the module's internal functionality.

### v1.3.12 (2025-06-09)

- **Changed**: Manage dependencies in pyproject.toml according to **PEP735**
- **Changed**: Removed pre-commit configuration file.

### v1.3.11 (2025-05-06)

- **Changed**: Manage dependencies from `pyproject.toml` instead of `requirements.txt`.
- **Changed:** Documentation examples to improve clarity and usability of `dump_fork`.

### v1.3.10 (2025-01-09)

- **Added:** Use custom logger for better control over logging output.
- **Changed**: Update the CI trigger to avoid runs on opened pull-request.

### v1.3.9 (2024-10-17)

- **Added:** More examples added to the documentation for clarity and completeness.

### v1.3.8 (2024-10-07)

- **Improved:** Documentation enhancements to improve readability and comprehensiveness.

### v1.3.7 (2024-10-04)

- **Added:** Automatic documentation generation using `mkdocs`.
- **Added:** Enhanced error messages for log loading to aid in troubleshooting.
- **Updated:** `pyproject.toml` file to include `ruff` linting rules for code quality.

### v1.3.6 (2024-10-03)

- **Fixed:** Corrected issues with the `pyproject.toml` file configuration.

### v1.3.5 (2024-10-03)

- **Updated:** Configuration migrated to a TOML file format for better maintainability.
- **Improved:** Added support for custom serialization/deserialization. Fixed `orjson` serialization issues.

### v1.3.4 (2024-09-30)

- **Added:** New parameter to allow passing an opener when loading files.
- **Added:** Ability to read JSONLines files with broken lines for fault tolerance.
- **Changed:** Stricter argument passing enforced using `/` and `*` in function signatures.

### v1.3.3 (2024-09-20)

- **Fixed:** The `dump_fork` function now ensures that files are properly closed after writing to prevent resource
  leaks.

### v1.3.1 (2024-09-20)

- **Updated:** Revised `README.md` and code docstrings to improve consistency and clarity.
- **Improved:** Optimized `dumper` function for better performance.

### v1.3.0 (2024-09-20)

- **Improved:** Enhanced `loader` and `dumper` functions for more efficient handling of both binary and text files.
- **Added:** The `dump` function now includes a `text_mode` argument for better control over file types.

### v1.2.0 (2024-09-20)

- **Added:** Support for the `.xz` compression format.
- **Updated:** Improvements to `README.md` and code docstrings for better documentation quality.
- **Added:** Configuration for `.pre-commit-config.yaml` to enforce code standards.

### v1.1.1 (2024-08-16)

- **Improved:** Added additional examples to `README.md` for better user guidance.

### v1.1.0 (2024-08-16)

- **Added:** Support for `orjson` and `ujson` libraries as alternatives to the standard `json` library.
- **Added:** Support for gzip-compressed JSON files (`.gz` and `.gzip`), as well as bzip2-compressed files (`.bz2`).
- **Breaking Change:** API simplified by removing `dump_into` and `load_from` functions. The `dump` and `load` functions
  now handle their functionality.
