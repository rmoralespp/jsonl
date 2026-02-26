# jsonl.dump_archive

Write multiple JSON Lines files into a ZIP or TAR archive. Supports compressed TAR variants
and custom serialization.

## Function Signature

```python
jsonl.dump_archive(
    path,
    data,
    *,
    opener=None,
    text_mode=True,
    dump_if_empty=True,
    json_dumps=None,
    **json_dumps_kwargs,
)
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path` | `str` | *(required)* | Destination path for the archive file |
| `data` | `Iterable[tuple[str, Iterable[Any]]]` | *(required)* | Iterable of `(relative_path, items)` tuples |
| `opener` | `Callable` or `None` | `None` | Custom function to open the given file paths |
| `text_mode` | `bool` | `True` | If `False`, write bytes instead of text |
| `dump_if_empty` | `bool` | `True` | If `False`, don't create empty files or an empty archive |
| `json_dumps` | `Callable` or `None` | `None` | Custom serialization function. Defaults to `json.dumps` |
| `**json_dumps_kwargs` | | | Additional keyword arguments passed to the serialization function |

### Returns

`str` or `None` — Path to the created archive file, or `None` if no items were written and `dump_if_empty` is `False`.

### Supported Archive Formats

| Extension | Format |
|---|---|
| `.zip` | ZIP |
| `.tar` | TAR (uncompressed) |
| `.tar.gz` | TAR + gzip |
| `.tar.bz2` | TAR + bzip2 |
| `.tar.xz` | TAR + xz |

!!! warning
    If the archive already exists at the given path, it will be **overwritten**.

!!! note
    - Paths in the `data` argument must be **relative**. Absolute paths will raise a `ValueError`.
    - If `data` contains multiple items for the same path, they are **appended** to the corresponding file within the archive.

---

## Examples

### Create a ZIP archive

```python
import jsonl

data = [
    ("users.jsonl", [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]),
    ("orders.jsonl", [{"id": 1, "total": 99.90}, {"id": 2, "total": 45.00}]),
]

jsonl.dump_archive("archive.zip", data)
```

### Create a compressed TAR archive

```python
import jsonl

data = [
    ("users.jsonl", [{"name": "Alice", "age": 30}]),
    ("logs/activity.jsonl", [{"event": "login", "ts": "2025-01-01T00:00:00Z"}]),
]

jsonl.dump_archive("archive.tar.gz", data)
```

### Compressed files inside the archive

Individual files within the archive can also be compressed:

```python
import jsonl

data = [
    ("file1.jsonl", [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]),
    ("path/to/file2.jsonl.gz", [{"name": "Charlie", "age": 35}]),
    ("file1.jsonl", [{"name": "Eve", "age": 28}]),  # Appends to file1.jsonl
]

jsonl.dump_archive("archive.zip", data)
```

### Skip empty files

```python
import jsonl

data = [
    ("has_data.jsonl", [{"value": 1}]),
    ("empty.jsonl", []),  # This file won't be created
]

# With dump_if_empty=False, empty files and empty archives are skipped
result = jsonl.dump_archive("archive.zip", data, dump_if_empty=False)
```
