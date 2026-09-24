# Changelog

All notable changes to this project are documented in the
[CHANGELOG.md](https://github.com/rmoralespp/jsonl/blob/main/CHANGELOG.md) file on GitHub.

---

## Latest Releases

### v1.5.3 (2026-09-25)

- **Added:** `open_stream` exposes local paths, URLs, and binary file-like objects as
  decompressed binary streams for incremental consumers; `load` reuses the same source-opening
  and decompression path.
- **Fixed:** Test warnings

### v1.5.2 (2026-09-9)

- **Added:** The CLI supports sequential record-count splitting with `--split N INPUT OUTPUT`.
- **Added:** `open_stream` exposes local paths, URLs, and binary file-like objects as
  decompressed binary streams for incremental consumers; `load` reuses the same source-opening
  and decompression path.
- **Added:** `load_archive` and the CLI now auto-discover `.jsonl` and `.ndjson` archive
  members, including supported compressed variants. Explicit member patterns remain unchanged.
- **Breaking Change:** `dump_fork` and `dump_archive` now limit open destination files to 64 by default. When the limit is reached, destinations are closed and reopened in append mode (`at`/`ab`). Custom `opener` functions must support append mode for destinations that may be reopened; pass `max_open_files=None` to retain the previous unbounded behavior.
- **Fixed:** Auto-detect archives from remote URLs in the CLI without `--member`


### v1.5.1 (2026-09-08)

- **Fixed:** `dump_archive` rejects archive member paths that escape the staging directory.
- **Fixed:** `dump_archive` supports archive filenames containing multiple dots.
- **Fixed:** `load` detects compressed data consistently for paths, URLs, and binary file-like objects.
- **Fixed:** File APIs consistently reject ambiguous `bytes` paths with a clear error.

### v1.5.0 (2026-09-07)

- **Added:** `jsonl` CLI with a `json`-style interface: stdin/stdout streaming, automatic
  compression, URLs, archive member auto-discovery and `--broken` record handling with well-defined exit codes.

### v1.4.2

- **Added:** `loads` - Deserialize a JSON Lines formatted string into an object iterator.
- **Added:** More tests to cover 100% of the codebase.
- **Added:** CONTRIBUTING.md
- **Changed:** Documentation - rewrite README and documentation for clarity and consistency
- **Changed:** Documentation - Remove redundant sections and fix code examples
- **Fixed:** warnings in CI/CD workflows

### v1.4.1

- **Fixed:** `json.JSONEncoder`/`json.JSONDecoder` is not callable

### v1.4.0

- **Breaking Change:** Increase similarity with Python standard library json module behavior:
  1. Now `load` and `load_archive` accept `cls` and `**kwargs` for custom decoding instead of `json_loads` and `**json_loads_kwargs`
  2. Now `dump`, `dump_fork`, `dumps` and `dump_archive` accept `cls` and `**kwargs` for custom encoding instead of `json_dumps` and `**json_dumps_kwargs`

### v1.3.27

- **Added:** Support for compression.zstd (Python 3.14+)

### v1.3.26

- **Added:** More tests to cover 100% of the codebase.
- **Fixed:** `load` Use context manager to close `TextIOWrapper` stream when loading from a URL.

### v1.3.25

- **Improved:** `load_archive` from URL no longer loads the file into RAM, reducing memory consumption. 
  Instead, the data is efficiently downloaded in chunks to a temporary file for loading.

### v1.3.24

- **Improved:** Moved internal `_openers` variable to module level, eliminating per-call dictionary allocation.
- **Improved:** `loader` by caching `isinstance(line, bytes)` check, evaluating only once instead of per iteration.
- **Improved:** `dump_archive` worker using `os.makedirs(exist_ok=True)` to eliminate race conditions and reduce syscalls.
- **Improved:** Streamlined `dump` function by combining `isinstance(file, (str, os.PathLike))` check with `os.fspath`.
- **Improved:** Removed redundant `iter()` call and improved `_looks_like_url` code structure for better readability.

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
