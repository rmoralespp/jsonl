<h1 align="center">jsonl</h1>
<p align="center">
  <img src="https://img.shields.io/pypi/v/py-jsonl.svg" alt="PyPI">
  <img src="https://img.shields.io/pypi/pyversions/py-jsonl.svg" alt="Python">
  <img src="https://github.com/rmoralespp/jsonl/workflows/CI/badge.svg" alt="CI">
  <img src="https://codecov.io/gh/rmoralespp/jsonl/branch/main/graph/badge.svg" alt="Coverage">
  <img src="https://img.shields.io/github/license/rmoralespp/jsonl.svg" alt="License">
</p>

<p align="center">
  <strong>Zero-dependency Python library for reading, writing, and compressing JSON Lines files.</strong>
</p>

<p align="center">
  <a href="https://rmoralespp.github.io/jsonl/">Documentation</a> ·
  <a href="https://github.com/rmoralespp/jsonl/blob/main/CHANGELOG.md">Changelog</a> ·
  <a href="https://pypi.org/project/py-jsonl/">PyPI</a>
</p>

```python
import jsonl

jsonl.dump([{"name": "Alice"}, {"name": "Bob"}], "file.jsonl.gz")

for item in jsonl.load("file.jsonl.gz"):
    print(item)
```

If you know `json.dump` and `json.load`, you already know **jsonl**.

---

## Install

```bash
pip install py-jsonl
```

> Python 3.8+ · No dependencies · Single file

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

> Fully compliant with [jsonlines.org](https://jsonlines.org/) and [ndjson](https://github.com/ndjson/ndjson-spec) specs.

---

## API

### Reading

| Function | Description |
|---|---|
| `jsonl.load(source, **kw)` | File, URL, or file-like → lazy iterator |
| `jsonl.load_archive(file, **kw)` | Unpack JSONL files from ZIP/TAR |
| `jsonl.loader(stream, broken, **kw)` | Low-level line-stream deserializer |

### Writing

| Function | Description |
|---|---|
| `jsonl.dump(iterable, file, **kw)` | Write to file (any format) |
| `jsonl.dumps(iterable, **kw)` | Serialize to string |
| `jsonl.dump_fork(paths, **kw)` | Write to multiple files at once |
| `jsonl.dump_archive(path, data, **kw)` | Pack into ZIP/TAR archive |
| `jsonl.dumper(iterable, **kw)` | Low-level generator → formatted lines |

> All functions accept `cls` and `**kwargs` for custom encoding/decoding.

[Full API docs →](https://rmoralespp.github.io/jsonl/)

---

## Examples

<details>
<summary><strong>Archives (ZIP / TAR)</strong></summary>

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

</details>

<details>
<summary><strong>Custom serializer (orjson)</strong></summary>

```python
import orjson
import jsonl

data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

jsonl.dump(data, "fast.jsonl", text_mode=False, cls=orjson.dumps)

for item in jsonl.load("fast.jsonl", cls=orjson.loads):
    print(item)
```

</details>

<details>
<summary><strong>Multiple output files</strong></summary>

```python
import jsonl

data = [
    ("a.jsonl", [{"x": 1}]),
    ("b.jsonl", [{"x": 2}]),
    ("a.jsonl", [{"x": 3}]),  # appends to a.jsonl
]
jsonl.dump_fork(data)
```

</details>

<details>
<summary><strong>Custom encoder/decoder classes</strong></summary>

```python
import datetime
import json
import jsonl

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        return super().default(obj)

data = [{"event": "launch", "date": datetime.date(2026, 1, 15)}]
jsonl.dump(data, "events.jsonl", cls=DateEncoder)
```

</details>

---

## Supported Formats

| Type | Extensions |
|---|---|
| Plain | `.jsonl` |
| Compressed | `.jsonl.gz` · `.jsonl.bz2` · `.jsonl.xz` · `.jsonl.zst`¹ |
| ZIP | `.zip` |
| TAR | `.tar` · `.tar.gz` · `.tar.bz2` · `.tar.xz` · `.tar.zst`¹ |

¹ Requires Python ≥ 3.14

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup, testing, and PR guidelines.

---

## License

[MIT](LICENSE)
