<h1 align="center">jsonl</h1>

<p align="center">
  <strong>Zero-dependency Python library for reading, writing, and compressing JSON Lines files.</strong>
</p>

<p align="center">
  <a href="https://pypi.python.org/pypi/py-jsonl"><img src="https://img.shields.io/pypi/v/py-jsonl.svg" alt="PyPI version"></a>
  <a href="https://github.com/rmoralespp/jsonl"><img src="https://img.shields.io/pypi/pyversions/py-jsonl.svg" alt="Python versions"></a>
  <a href="https://github.com/rmoralespp/jsonl/actions?query=event%3Arelease+workflow%3ACI"><img src="https://github.com/rmoralespp/jsonl/workflows/CI/badge.svg" alt="CI"></a>
  <a href="https://app.codecov.io/gh/rmoralespp/jsonl"><img src="https://codecov.io/gh/rmoralespp/jsonl/branch/main/graph/badge.svg" alt="Coverage"></a>
  <a href="https://github.com/rmoralespp/jsonl/blob/main/LICENSE"><img src="https://img.shields.io/github/license/rmoralespp/jsonl.svg" alt="License"></a>
</p>

---

```python
import jsonl

jsonl.dump([{"name": "Alice"}, {"name": "Bob"}], "file.jsonl.gz")

for item in jsonl.load("file.jsonl.gz"):
    print(item)
```

If you know `json.dump` and `json.load`, you already know **jsonl**.

---

## Features

- **Familiar API** — same `dump`/`load` interface as Python's `json` module.
- **Streaming by default** — iterators in, iterators out. Constant memory.
- **Automatic compression** — `.gz`, `.bz2`, `.xz`, `.zst` (Python ≥ 3.14). Detected by extension or [magic bytes](https://en.wikipedia.org/wiki/List_of_file_signatures).
- **Archive support** — read/write `.zip`, `.tar.gz`, `.tar.bz2`, `.tar.xz` natively.
- **URL loading** — pass a URL to `load()` or `load_archive()` directly.
- **Pluggable serialization** — swap in `orjson`, `ujson`, or any encoder/decoder via `cls`.
- **Error tolerance** — skip malformed lines instead of crashing.
- **Zero dependencies** — pure standard library; single `.py` file you can vendor.

Fully compliant with the [JSON Lines](https://jsonlines.org/) and [NDJSON](https://github.com/ndjson/ndjson-spec) specifications.

---

## Quick Start

### Install

```bash
pip install py-jsonl
```

!!! note
    Requires **Python 3.8+**. No external dependencies.

### Write and read

```python
import jsonl

# Write to plain or compressed files
jsonl.dump([{"name": "Alice"}, {"name": "Bob"}], "users.jsonl")
jsonl.dump([{"key": "value"}], "data.jsonl.gz")

# Read (lazy iterator — constant memory)
for user in jsonl.load("users.jsonl"):
    print(user)

# Read from a URL
for item in jsonl.load("https://example.com/data.jsonl"):
    print(item)
```

### Archives

```python
import jsonl

data = [
    ("users.jsonl", [{"name": "Alice"}, {"name": "Bob"}]),
    ("orders.jsonl", [{"id": 1, "total": 99.90}]),
]
jsonl.dump_archive("data.tar.gz", data)

for filename, items in jsonl.load_archive("data.tar.gz"):
    for item in items:
        print(filename, item)
```

### Custom serialization

```python
import orjson
import jsonl

data = [{"name": "Alice", "age": 30}]

jsonl.dump(data, "fast.jsonl", text_mode=False, cls=orjson.dumps)

for item in jsonl.load("fast.jsonl", cls=orjson.loads):
    print(item)
```

---

## API Overview

### Reading

| Function                                | Description                                       |
|-----------------------------------------|---------------------------------------------------|
| [`jsonl.load`](load.md)                 | File, URL, or file-like → lazy iterator           |
| [`jsonl.loads`](loads.md)               | JSON Lines string → lazy iterator                 |
| [`jsonl.load_archive`](load_archive.md) | Unpack JSONL files from ZIP/TAR archive           |
| [`jsonl.loader`](loader.md)             | Low-level line-stream deserializer                |

### Writing

| Function                                | Description                                       |
|-----------------------------------------|---------------------------------------------------|
| [`jsonl.dump`](dump.md)                 | Write to file (any format)                        |
| [`jsonl.dumps`](dumps.md)               | Serialize to string                               |
| [`jsonl.dump_fork`](dump_fork.md)       | Write to multiple files at once                   |
| [`jsonl.dump_archive`](dump_archive.md) | Pack into ZIP/TAR archive                         |
| [`jsonl.dumper`](dumper.md)             | Low-level generator → formatted lines             |

!!! tip "Custom Serialization"
    All functions accept `cls` and `**kwargs` for custom encoding/decoding.

---

## Supported Formats

| Type       | Extensions                                                            |
|------------|-----------------------------------------------------------------------|
| Plain      | `.jsonl`                                                              |
| Compressed | `.jsonl.gz` · `.jsonl.bz2` · `.jsonl.xz` · `.jsonl.zst`¹            |
| ZIP        | `.zip`                                                                |
| TAR        | `.tar` · `.tar.gz` · `.tar.bz2` · `.tar.xz` · `.tar.zst`¹           |

¹ Requires Python ≥ 3.14

!!! info
    When reading, if the file extension is not recognized, **jsonl** falls back to
    [magic-number detection](https://en.wikipedia.org/wiki/List_of_file_signatures)
    to identify the compression format automatically.

---

## License

MIT — see [LICENSE](https://github.com/rmoralespp/jsonl/blob/main/LICENSE) for details.
