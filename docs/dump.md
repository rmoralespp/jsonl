# jsonl.dump

Write an iterable of objects to a JSON Lines file. Supports filenames (with automatic compression),
`os.PathLike` objects, and file-like objects with `write` or `writelines` methods.

## Function Signature

```python
jsonl.dump(
    iterable,
    file,
    *,
    opener=None,
    text_mode=True,
    json_dumps=None,
    **json_dumps_kwargs,
)
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `iterable` | `Iterable[Any]` | *(required)* | Iterable of JSON-serializable objects |
| `file` | `str`, `PathLike`, file-like | *(required)* | Destination file path or file-like object |
| `opener` | `Callable` or `None` | `None` | Custom function to open the file (used only when `file` is a path) |
| `text_mode` | `bool` | `True` | If `False`, write bytes instead of text |
| `json_dumps` | `Callable` or `None` | `None` | Custom serialization function. Defaults to `json.dumps` |
| `**json_dumps_kwargs` | | | Additional keyword arguments passed to the serialization function |

### Raises

| Exception | Condition |
|---|---|
| `ValueError` | If the file object is missing both `writelines` and `write` methods |

### Compression Detection

!!! note
    Supported compression formats: **gzip (.gz), bzip2 (.bz2), xz (.xz)**

    When a filename is provided, the compression format is determined by its extension.
    If the extension is not recognized, the file is written as plain text.

---

## Examples

### Write to a file

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "file.jsonl")
```

### Write to a compressed file

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "file.jsonl.gz")    # gzip
jsonl.dump(data, "file.jsonl.bz2")   # bzip2
jsonl.dump(data, "file.jsonl.xz")    # xz
```

### Write to an open file object

!!! tip
    Useful when you need fine-grained control over how the file is opened, or when appending to an existing file.

```python
import gzip
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Text file
with open("file.jsonl", mode="wt", encoding="utf-8") as fd:
    jsonl.dump(data, fd, text_mode=True)

# Binary compressed file
with gzip.open("file.jsonl.gz", mode="wb") as fd:
    jsonl.dump(data, fd, text_mode=False)
```

### Append to an existing file

```python
import gzip
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Append to a compressed file
with gzip.open("file.jsonl.gz", mode="ab") as fp:
    jsonl.dump(data, fp, text_mode=False)

# Append to an uncompressed file
with open("file.jsonl", mode="at", encoding="utf-8") as fp:
    jsonl.dump(data, fp, text_mode=True)
```

### Write to a custom file object

!!! tip
    The custom file object must implement a `write` or `writelines` method.

```python
import jsonl


class MyWriter:
    """A custom file object with a writelines method."""

    def writelines(self, lines):
        for line in lines:
            print(line, end="")


data = [{"name": "Alice"}, {"name": "Bob"}]

jsonl.dump(data, MyWriter(), text_mode=True)
```

### Custom serialization

#### Using a third-party library

[`orjson`](https://github.com/ijl/orjson) is a high-performance JSON library that returns bytes:

```python
import orjson
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# orjson returns bytes — set text_mode=False
jsonl.dump(data, "file.jsonl", json_dumps=orjson.dumps, text_mode=False)
```

#### Passing additional keyword arguments

Extra keyword arguments are forwarded directly to the serialization function (by default, `json.dumps`):

```python
import jsonl

data = [{"name": "Alice", "score": 9.5}, {"name": "Bob", "score": 7.2}]

# Compact output (minimal whitespace)
jsonl.dump(data, "compact.jsonl", separators=(",", ":"))

# Sorted keys for deterministic output
jsonl.dump(data, "sorted.jsonl", sort_keys=True)
```
