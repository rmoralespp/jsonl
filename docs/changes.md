# Changelog

All notable changes to this project are documented in the
[CHANGELOG.md](https://github.com/rmoralespp/jsonl/blob/main/CHANGELOG.md) file on GitHub.

---

## Latest Releases

### v1.3.23

- **Changed:** Documentation - Use `zensical` instead `mkdocs` for documentation generation.

### v1.3.22

- Improved documentation examples for `json.dump` and `json.load` keyword arguments.
- Enabled additional `ruff` linting rules and passed all checks.
- Enhanced docstrings with full `sphinx-linter` compliance.

### v1.3.21

- Added `sphinx-linter` and `pymport` linters to CI/CD pipeline.
- Updated `README.md` badges for better visibility.

### v1.3.20

- Added support for Python 3.14.

### v1.3.19

- Improved compression detection: `load_archive` and `load` now use magic-number detection as fallback.

### v1.3.18

- Replaced deprecated `urllib.request.urlretrieve` with modern alternative.

### v1.3.17

- `load_archive` now supports loading directly from URLs.
- Added acceptance tests for URL-based loading with a local HTTP server.

### v1.3.16

- `load` now supports loading directly from URLs.
- `dump_archive` and `dump_fork` now accept `pathlib.Path` objects.

### v1.3.14

- Added `dump_archive` function for writing archives.

### v1.3.13

- Added `load_archive` function for reading archives.
- Reached 100% test coverage.

---

For the complete history, see the [full changelog on GitHub](https://github.com/rmoralespp/jsonl/blob/main/CHANGELOG.md).
