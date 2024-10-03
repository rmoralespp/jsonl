## Releases ##

- **Changed:** Setup using a TOML file.
- **Changed:** Supports custom serialization/deserialization. Fix `orjson` serialization.

## v1.3.4 (2024-09-30) ##

- **Added:** Allow passing an opener as a parameter.
- **Added:** Allow reading JSONLines files with broken lines.
- **Changed:** Using `/` and `*` in function definitions is a stricter way to specify how arguments are passed.

## v1.3.3 (2024-09-20) ##

- **Changed:** Update `dump_fork` function to ensure that the files are closed after writing.

## v1.3.1 (2024-09-20) ##

- **Changed:** Update `README.md` and code docstrings.
- **Changed:** Update `dumper` function.

## v1.3.0 (2024-09-20) ##

- **Changed:** Improve `loader` and `dumper` functions to handle binary/text files more efficiently.
- **Changed:** `dump` function now accepts a `text_mode` argument to write text files or binary files.

## v1.2.0 (2024-09-20) ##

- **Added:** Supports `.xz` compression format.
- **Changed:** Update `README.md` and code docstrings.
- **Added:** Configure `.pre-commit-config.yaml` file

## v1.1.1 (2024-08-16) ##

- **Changed:** Adding more examples to `README.md`

## v1.1.0 (2024-08-16) ##

- **Added:** Support for `orjson` and `ujson` libraries, in addition to the standard `json` library.
- **Added:** Supports `.gz` and `.gzip` for gzip-compressed JSON files, and `.bz2` for bzip2-compressed JSON files.
- **Breaking-Changed:** Simplified API by removing `dump_into` and `load_from` functions. The `dump` and `load`
  functions now
  encompass the functionality of `dump_into` and `load_from`.
