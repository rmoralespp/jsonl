# jsonl

<p align="center">
  <em>A lightweight, dependency-free Python library for reading, writing, and streaming JSON Lines data.</em>
</p>

<p align="center">
  <a href="https://pypi.python.org/pypi/py-jsonl"><img src="https://img.shields.io/pypi/v/py-jsonl.svg" alt="PyPI version"></a>
  <a href="https://github.com/rmoralespp/jsonl"><img src="https://img.shields.io/pypi/pyversions/py-jsonl.svg" alt="Python versions"></a>
  <a href="https://github.com/rmoralespp/jsonl/actions?query=event%3Arelease+workflow%3ACI"><img src="https://github.com/rmoralespp/jsonl/workflows/CI/badge.svg" alt="CI"></a>
  <a href="https://app.codecov.io/gh/rmoralespp/jsonl"><img src="https://codecov.io/gh/rmoralespp/jsonl/branch/main/graph/badge.svg" alt="Coverage"></a>
  <a href="https://github.com/rmoralespp/jsonl/blob/main/LICENSE"><img src="https://img.shields.io/github/license/rmoralespp/jsonl.svg" alt="License"></a>
  <a href="https://pepy.tech/project/py-jsonl"><img src="https://pepy.tech/badge/py-jsonl" alt="Downloads"></a>
</p>

---

**jsonl** provides a simple, Pythonic API for working with [JSON Lines](https://jsonlines.org/) data.
It follows the conventions of Python's standard `json` module — if you know `json.dump` and `json.load`,
you already know how to use **jsonl**.

Fully compliant with the [JSON Lines](https://jsonlines.org/) and [NDJSON](https://github.com/ndjson/ndjson-spec)
specifications.

---

## Why jsonl?

The [JSON Lines](https://jsonlines.org/) format is ideal for processing large volumes of structured data line by line,
without loading everything into memory. **jsonl** lets you work with this format effortlessly, offering a familiar API
inspired by Python's standard `json` module — with zero external dependencies.

## Features

| Feature                        | Description                                                                |
|--------------------------------|----------------------------------------------------------------------------|
| 🌎 **Familiar API**            | Interface similar to the standard `json` module (`dump`, `load`, `dumps`)  |
| ⚡ **Streaming by default**     | Read and write incrementally via iterators, keeping memory usage low       |
| 🗜️ **Built-in compression**   | Transparent support for `gzip`, `bzip2`, and `xz`                          |
| 📦 **Archive support**         | Read and write `ZIP` and `TAR` archives (`.tar.gz`, `.tar.bz2`, `.tar.xz`) |
| 📥 **Load from URLs**          | Pass a URL directly to `load()` or `load_archive()`                        |
| 🚀 **Pluggable serialization** | Swap in [`orjson`](https://github.com/ijl/orjson), or any JSON library     |
| 🔧 **Error tolerance**         | Optionally skip malformed lines instead of crashing                        |
| 🐍 **Zero dependencies**       | Uses only the Python standard library — nothing else                       |

## Quick Start

### Install

```bash
pip install py-jsonl
```

!!! note
Requires **Python 3.8** or higher. No external dependencies needed.

### Write data

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "players.jsonl")
```

### Read data

```python
import jsonl

for item in jsonl.load("players.jsonl"):
    print(item)
```

### Read from a URL

```python
import jsonl

for item in jsonl.load("https://example.com/data.jsonl"):
    print(item)
```

### Compressed files

The compression format is detected automatically — by file extension when writing,
and by [magic numbers](https://en.wikipedia.org/wiki/List_of_file_signatures) when reading:

```python
import jsonl

data = [{"key": "value"}]

jsonl.dump(data, "file.jsonl.gz")  # gzip
jsonl.dump(data, "file.jsonl.bz2")  # bzip2
jsonl.dump(data, "file.jsonl.xz")  # xz

for item in jsonl.load("file.jsonl.gz"):
    print(item)
```

### Archives (ZIP / TAR)

```python
import jsonl

# Write multiple files into an archive
data = [
    ("users.jsonl", [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]),
    ("orders.jsonl", [{"id": 1, "total": 99.90}, {"id": 2, "total": 45.00}]),
]
jsonl.dump_archive("data.tar.gz", data)

# Read them back
for filename, items in jsonl.load_archive("data.tar.gz"):
    print(f"--- {filename} ---")
    for item in items:
        print(item)
```

---

## API Overview

### Reading

| Function                                | Description                                                     |
|-----------------------------------------|-----------------------------------------------------------------|
| [`jsonl.load`](load.md)                 | Read a file, URL, or file-like object as an iterator of objects |
| [`jsonl.load_archive`](load_archive.md) | Read JSON Lines files from a ZIP or TAR archive                 |

### Writing

| Function                                | Description                                              |
|-----------------------------------------|----------------------------------------------------------|
| [`jsonl.dump`](dump.md)                 | Write an iterable of objects to a JSON Lines file        |
| [`jsonl.dumps`](dumps.md)               | Serialize an iterable into a JSON Lines string           |
| [`jsonl.dump_fork`](dump_fork.md)       | Write to multiple JSON Lines files simultaneously        |
| [`jsonl.dump_archive`](dump_archive.md) | Pack multiple JSON Lines files into a ZIP or TAR archive |

!!! tip "Custom Serialization"
All **write** functions accept `json_dumps` and `**json_dumps_kwargs` for custom serialization.
All **read** functions accept `json_loads` and `**json_loads_kwargs` for custom deserialization.

## Supported Formats

| Type        | Extensions                               |
|-------------|------------------------------------------|
| Plain       | `.jsonl`                                 |
| Compressed  | `.jsonl.gz`, `.jsonl.bz2`, `.jsonl.xz`   |
| ZIP archive | `.zip`                                   |
| TAR archive | `.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz` |

!!! info
When reading, if the file extension is not recognized, **jsonl** falls back to
[magic-number detection](https://en.wikipedia.org/wiki/List_of_file_signatures)
to identify the compression format automatically.

## License

MIT — see [LICENSE](https://github.com/rmoralespp/jsonl/blob/main/LICENSE) for details.
