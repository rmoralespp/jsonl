<p align="center">
  <strong>jsonl</strong>
</p>

<p align="center">
  <em>A lightweight, dependency-free Python library for JSON Lines — read, write, compress, and stream with ease.</em>
</p>

<p align="center">
  <a href="https://pypi.python.org/pypi/py-jsonl"><img src="https://img.shields.io/pypi/v/py-jsonl.svg" alt="PyPI version"></a>
  <a href="https://github.com/rmoralespp/jsonl"><img src="https://img.shields.io/pypi/pyversions/py-jsonl.svg" alt="Python versions"></a>
  <a href="https://github.com/rmoralespp/jsonl/actions?query=event%3Arelease+workflow%3ACI"><img src="https://github.com/rmoralespp/jsonl/workflows/CI/badge.svg" alt="CI"></a>
  <a href="https://app.codecov.io/gh/rmoralespp/jsonl"><img src="https://codecov.io/gh/rmoralespp/jsonl/branch/main/graph/badge.svg" alt="Coverage"></a>
  <a href="https://github.com/rmoralespp/jsonl/blob/main/LICENSE"><img src="https://img.shields.io/github/license/rmoralespp/jsonl.svg" alt="License"></a>
  <a href="https://pepy.tech/project/py-jsonl"><img src="https://pepy.tech/badge/py-jsonl" alt="Downloads"></a>
</p>

<p align="center">
  <a href="https://rmoralespp.github.io/jsonl/">Documentation</a>
  ·
  <a href="https://github.com/rmoralespp/jsonl/blob/main/CHANGELOG.md">Changelog</a>
  ·
  <a href="https://github.com/rmoralespp/jsonl/issues">Issues</a>
</p>

---

**jsonl** provides a simple, Pythonic API for working with [JSON Lines](https://jsonlines.org/) data.
It follows the conventions of Python's standard `json` module — if you know `json.dump` and `json.load`,
you already know how to use **jsonl**.

Fully compliant with the [jsonlines](https://jsonlines.org/) and [ndjson](https://github.com/ndjson/ndjson-spec)
specifications.

## Features

| Feature                        | Description                                                                                                     |
|--------------------------------|-----------------------------------------------------------------------------------------------------------------|
| 🌎 **Familiar API**            | Interface similar to the standard `json` module (`dump`, `load`, `dumps`)                                       |
| ⚡ **Streaming by default**     | Read and write incrementally via iterators, keeping memory usage low                                            |
| 🗜️ **Built-in compression**   | Transparent support for `gzip`, `bzip2`, `xz`, and `zst` (Python ≥ 3.14)                                        |
| 📦 **Archive support**         | Read and write `ZIP` and `TAR` archives (`.tar.gz`, `.tar.bz2`, `.tar.xz`, and `.tar.zst` **(Python ≥ 3.14) )** |
| 📥 **Load from URLs**          | Pass a URL directly to `load()` or `load_archive()`                                                             |
| 🚀 **Pluggable serialization** | Swap in [`orjson`](https://github.com/ijl/orjson), or any JSON library                                          |
| 🔧 **Error tolerance**         | Optionally skip malformed lines instead of crashing                                                             |
| 🐍 **Zero dependencies**       | Uses only the Python standard library — nothing else                                                            |

## Installation

```bash
pip install py-jsonl
```

> Requires **Python 3.8+**. No external dependencies.

## Quick Start

### Write

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "players.jsonl")
```

### Read

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

The compression format is determined automatically — by file extension when writing,
and by [magic numbers](https://en.wikipedia.org/wiki/List_of_file_signatures) when reading
if the file extension is not recognized:

```python
import jsonl

data = [{"key": "value"}]

jsonl.dump(data, "file.jsonl.gz")  # gzip
jsonl.dump(data, "file.jsonl.bz2")  # bzip2
jsonl.dump(data, "file.jsonl.xz")  # xz
jsonl.dump(data, "file.jsonl.zst")  # zst (Python ≥ 3.14) 

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

### Multiple output files

```python
import jsonl

data = [
    ("file1.jsonl", [{"name": "Alice"}, {"name": "Bob"}]),
    ("file2.jsonl", [{"name": "Charlie"}]),
    ("file1.jsonl", [{"name": "Eve"}]),  # appended to file1.jsonl
]

jsonl.dump_fork(data)
```

## API Overview

### Reading

| Function                             | Description                                       |
|--------------------------------------|---------------------------------------------------|
| `jsonl.load(source, **kw)`           | Read from a file, URL, or file-like object        |
| `jsonl.load_archive(file, **kw)`     | Unpack JSON Lines files from a ZIP or TAR archive |
| `jsonl.loader(stream, broken, **kw)` | Low-level generator deserializing a line stream   |

> [!TIP]
> All **read** functions accept `json_loads` and `**json_loads_kwargs` for custom deserialization.

### Writing

| Function                               | Description                                              |
|----------------------------------------|----------------------------------------------------------|
| `jsonl.dump(iterable, file, **kw)`     | Write objects to a JSON Lines file                       |
| `jsonl.dumps(iterable, **kw)`          | Serialize to a JSON Lines string                         |
| `jsonl.dump_fork(paths, **kw)`         | Write to multiple JSON Lines files at once               |
| `jsonl.dump_archive(path, data, **kw)` | Pack multiple JSON Lines files into a ZIP or TAR archive |
| `jsonl.dumper(iterable, **kw)`         | Low-level generator yielding formatted lines             |

> [!TIP]
> All **write** functions accept `json_dumps` and `**json_dumps_kwargs` for custom serialization.

For complete parameter documentation, see the [full docs →](https://rmoralespp.github.io/jsonl/)

## Custom Serialization

Plug in any JSON-compatible serializer.


For example, [`orjson`](https://github.com/ijl/orjson) for high-performance encoding:

```python
import orjson  # ensure orjson is installed: pip install orjson
import jsonl

data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

# Write with orjson (returns bytes → set text_mode=False)
jsonl.dump(data, "fast.jsonl", text_mode=False, cls=orjson.dumps)

# Read with orjson
for item in jsonl.load("fast.jsonl", cls=orjson.loads):
    print(item)
```

Another example: using custom `JSONEncoder` or `JSONDecoder` with `**kwargs` for various purposes, for example:


```python
import datetime
import decimal
import json

import jsonl


class UpperDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, object_hook=self.object_hook, parse_float=decimal.Decimal, **kwargs)

    def object_hook(self, obj):
        return {k.upper(): v for k, v in obj.items()}


class ISODateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return super().default(obj)


data = [
    {"name": "Alice", "birthdate": datetime.date(2000, 1, 1)},
    {"name": "Bob", "birthdate": datetime.date(2005, 1, 1)}
]

#  Write using a custom encoder to serialize datetime objects as ISO strings
jsonl.dump(data, "fast.jsonl", cls=ISODateEncoder)

# Read using a custom decoder to convert floats into Decimal and uppercase all keys
for item in jsonl.load("fast.jsonl", cls=UpperDecoder):
    print(item)
```

keyword arguments are forwarded to the underlying serializer:

```python
import jsonl

data = [{"name": "Alice", "score": 9.5}, {"name": "Bob", "score": 7.2}]

jsonl.dump(data, "compact.jsonl", separators=(",", ":"))  # compact output
jsonl.dump(data, "sorted.jsonl", sort_keys=True)  # deterministic keys
```

## Supported Formats

| Type        | Extensions                                                           |
|-------------|----------------------------------------------------------------------|
| Plain       | `.jsonl`                                                             |
| Compressed  | `.jsonl.gz`, `.jsonl.bz2`, `.jsonl.xz`, `.jsonl.zst` (Python ≥ 3.14) |
| ZIP archive | `.zip`                                                               |
| TAR archive | `.tar`, `.tar.gz`, `.tar.bz2`, `.tar.xz`, `.tar.zst` (Python ≥ 3.14) |

> When reading, if the file extension is not recognized, **jsonl** falls back to
> [magic-number detection](https://en.wikipedia.org/wiki/List_of_file_signatures)
> to identify the compression format automatically.

## Contributing

```bash
# Install dev dependencies
pip install --group=test --upgrade

# Run tests
python -m pytest tests/
python -m pytest tests/ --cov  # run with coverage reporting

# Lint
pip install --group=lint --upgrade
ruff check .

# Docs
pip install --group=doc --upgrade

# zensical usage: https://zensical.org/docs/usage/
zensical build 
zensical serve
```

## License

MIT — see [LICENSE](LICENSE) for details.
