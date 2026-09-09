# Command-line interface

Installing **jsonl** adds a `jsonl` command (equivalently `python -m jsonl`) that brings the
library's streaming, compression, URL, and archive features to the shell — no Python code needed.

```text
jsonl [OPTIONS] [INFILE] [OUTFILE]
```

| Argument  | Description                                                             |
|-----------|-------------------------------------------------------------------------|
| `INFILE`  | Input file, archive (ZIP or TAR), or URL. Reads from **stdin** when omitted or `-`.  |
| `OUTFILE` | Output file. Writes to **stdout** when omitted.                         |

Input is processed as a **stream**, so memory stays constant regardless of size. Compression is
handled automatically: the output codec is chosen from the file extension (`.gz`, `.bz2`, `.xz`,
`.zst` *Python ≥ 3.14*), and input compression is detected from the extension or the first bytes
([magic numbers](https://en.wikipedia.org/wiki/List_of_file_signatures)) — including stdin and URLs.

## Options

| Option             | Description                                                                                    |
|--------------------|------------------------------------------------------------------------------------------------|
| `--compact`        | Write records in the most compact form (no spaces).                                            |
| `--sort-keys`      | Sort object keys alphabetically.                                                               |
| `--ascii`          | Escape non-ASCII characters as `\uXXXX`. Output is raw UTF-8 by default.                       |
| `--member PATTERN` | Pick local or remote archive members by shell-style pattern. Without it, archives auto-select recognized `.jsonl`/`.ndjson` members and their supported compressed variants.|
| `--broken`         | Skip invalid records instead of aborting (see [Error handling](#error-handling)).             |
| `--split N`        | Write at most `N` records per output file.                                                     |
| `--version`        | Show the version and exit.                                                                     |
| `-h`, `--help`     | Show the help message and exit.                                                                |

## Examples

```bash
# Validate and pretty-pass a file (aborts on the first invalid record)
jsonl data.jsonl

# Convert between files; compression follows the extension (gzip in, zstd out)
jsonl data.jsonl.gz data.jsonl.zst

# Pipe through a shell pipeline
cat data.jsonl | jsonl --compact > compact.jsonl

# Load directly from a URL (auto-decompressed)
jsonl https://example.com/data.jsonl.gz > data.jsonl

# Read an archive: recognized JSONL/NDJSON members are auto-discovered and streamed
jsonl dataset.zip > merged.jsonl

# Remote archives are detected from their content, even without a file extension
jsonl 'https://example.com/download?id=123' > merged.jsonl

# Select specific members from an archive
jsonl --member '2026/*.jsonl' dataset.tar.gz > year.jsonl

# Tolerate broken input: skip invalid records and report them to stderr
jsonl --broken messy.jsonl clean.jsonl

# Split into 50,000-record gzip files
jsonl --split 50000 input.jsonl users.jsonl.gz

# Reformat: sort keys and escape non-ASCII to pure ASCII
jsonl --sort-keys --ascii data.jsonl > normalized.jsonl
```

## Splitting

`--split N` streams the input into sequential files of at most `N` records. Indexing starts at `00000` and uses five
zero-padded digits. The index is inserted before a recognized JSONL or NDJSON suffix, preserving compression:
`users.jsonl.gz` creates `users-00000.jsonl.gz`, `users-00001.jsonl.gz`, and so on.

Splitting uses the existing incremental multipath writer with one open destination at a time. It does not create a
manifest and does not publish all shards atomically: if input processing fails, files already written remain available.

!!! info "No `--indent`"
    Spreading a value across multiple lines would break the JSON Lines format (one value per
    line), so `--indent` is intentionally unsupported.

## Error handling

<a id="error-handling"></a>

By default the **first** invalid record aborts processing. With `--broken`, invalid records are
skipped and reported to stderr (with the input line number when available) while the rest continue.
`--broken` covers only recoverable JSON parsing errors; I/O, filesystem, archive, and compression
errors always abort.

!!! tip "Atomic output files"
    When writing to a file without `--split`, output goes to a temporary file that **atomically** replaces the
    destination only after the whole input succeeds — a failed run never leaves a partial file,
    and the existing destination is untouched. Input and output may not be the same file. When
    writing to **stdout**, valid records may already be emitted before an error, since stdout
    cannot be rolled back.

### Exit codes

| Code | Meaning                                                             |
|------|---------------------------------------------------------------------|
| `0`  | Success — all records valid.                                        |
| `1`  | One or more invalid JSON records.                                   |
| `2`  | Invalid command-line usage or configuration.                        |
| `3`  | Unexpected I/O, filesystem, archive, compression, or runtime error. |

!!! note "Non-UTF-8 terminals"
    Output is UTF-8 by default (like `jq`) and written as UTF-8 regardless of locale, so redirects
    and pipes always get valid bytes. A legacy non-UTF-8 console may *display* non-ASCII as mojibake
    (a rendering issue, not corruption) — use `--ascii`, or switch the console to UTF-8
    (`chcp 65001` on Windows).
