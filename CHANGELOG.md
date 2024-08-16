## Releases ##

## v1.1.0 (2024-08-16) ##

- **Added:** Support for `orjson` and `ujson` libraries, in addition to the standard `json` library.
- **Added:** Supports `.gz` and `.gzip` for gzip-compressed JSON files, and `.bz2` for bzip2-compressed JSON files.
- **Breaking-Changed:** Simplified API by removing `dump_into` and `load_from` functions. The `dump` and `load` functions now
encompass the functionality of `dump_into` and `load_from`.