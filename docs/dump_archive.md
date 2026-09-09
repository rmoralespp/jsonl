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
    max_open_files=64,
    cls=None,
    **kwargs,
)
```

### Parameters

| Parameter       | Type                                          | Default            | Description                                               |
|-----------------|-----------------------------------------------|--------------------|-----------------------------------------------------------|
| `path`          | `str`, `PathLike[str]`                         | *(required)*       | Destination path for the archive file                     |
| `data`          | `Iterable[tuple[str | PathLike[str], Iterable[Any]]]` | *(required)* | Iterable of `(relative_path, items)` tuples |
| `opener`        | `Callable` or `None`                          | `None`             | Custom function to open the given file paths              |
| `text_mode`     | `bool`                                        | `True`             | If `False`, write bytes instead of text                   |
| `dump_if_empty` | `bool`                                        | `True`             | If `False`, don't create empty files or an empty archive  |
| `max_open_files` | `int` or `None`                              | `64`               | Maximum number of open members; `None` disables the limit |
| `cls`           | `type[json.JSONEncoder]` `Callable` or `None` | `json.JSONEncoder` | Custom encoder                                            |
| `**kwargs`      |                                               |                    | Additional keyword arguments passed to the `cls`  encoder |

### Returns

`str` or `None` — Path to the created archive file, or `None` if no items were written and `dump_if_empty` is `False`.

### Supported Archive Formats

| Extension  | Format                    |
|------------|---------------------------|
| `.zip`     | ZIP                       |
| `.tar`     | TAR (uncompressed)        |
| `.tar.gz`  | TAR + gzip                |
| `.tar.bz2` | TAR + bzip2               |
| `.tar.xz`  | TAR + xz                  |
| `.tar.zst` | TAR + zst (Python ≥ 3.14) |

!!! warning
    If the archive already exists at the given path, it will be **overwritten**.

!!! note
    - Paths in the `data` argument must be **relative** and remain within the archive staging directory.
      Absolute paths and paths that escape through `..` components raise a `ValueError`.
    - Raw `bytes` paths and `PathLike` objects returning bytes are rejected; decode them with `os.fsdecode()` first.
    - If `data` contains multiple items for the same path, they are **appended** to the corresponding file within the
      archive.
    - At most `max_open_files` member files remain open. Least recently used members are closed and reopened in append
      mode when needed. Pass `None` to disable the limit; frequent reopening of compressed members can reduce
      compression efficiency.
    - Custom openers must support write and append modes when members are reopened.

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
