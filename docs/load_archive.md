# jsonl.load_archive

Load multiple JSON Lines files from a ZIP or TAR archive incrementally.

## Function Signature

```python
jsonl.load_archive(
    file,
    *,
    pattern="*.jsonl",
    pwd=None,
    opener=None,
    broken=False,
    json_loads=None,
    **json_loads_kwargs,
)
```

### Parameters

| Parameter             | Type                                           | Default      | Description                                                              |
|-----------------------|------------------------------------------------|--------------|--------------------------------------------------------------------------|
| `file`                | `str`, `PathLike`, `URL`, `Request`, file-like | *(required)* | Archive file to load from                                                |
| `pattern`             | `str`                                          | `"*.jsonl"`  | Unix shell-style wildcard pattern to filter filenames inside the archive |
| `pwd`                 | `bytes` or `None`                              | `None`       | Password to decrypt the archive (ZIP only)                               |
| `opener`              | `Callable` or `None`                           | `None`       | Custom function to open the file (not supported for URLs)                |
| `broken`              | `bool`                                         | `False`      | If `True`, skip malformed lines and log a warning                        |
| `json_loads`          | `Callable` or `None`                           | `None`       | Custom deserialization function. Defaults to `json.loads`                |
| `**json_loads_kwargs` |                                                |              | Additional keyword arguments passed to the deserialization function      |

### Returns

`Iterator[tuple[str, Iterator[Any]]]` — An iterator of `(filename, items)` tuples, where `items` is an iterator of
deserialized objects.

### Supported Archive Formats

- **ZIP** archives (`.zip`)
- **TAR** archives (`.tar`), including compressed variants: `.tar.gz`, `.tar.bz2`, `.tar.xz`

### Key Features

- Load from local files or remote URLs
- Filter files inside the archive using [Unix shell-style wildcards](https://docs.python.org/3/library/fnmatch.html)
- Support for compressed `.jsonl` files inside the archive (e.g., `.jsonl.gz`, `.jsonl.bz2`, `.jsonl.xz`).
  Check [compression detection](load.md#note-compression) for details.
- ZIP archives with password protection
- Graceful handling of malformed lines via the `broken` parameter

---

## Examples

### Load from a local archive

```python
import jsonl

for filename, items in jsonl.load_archive("archive.zip"):
    print(f"--- {filename} ---")
    for item in items:
        print(item)
```

### Load from a remote archive (URL)

You can load archives from a URL. For custom request headers, use `urllib.request.Request`:

```python
import urllib.request
import jsonl

# Load directly from a URL
for filename, items in jsonl.load_archive("https://example.com/archive.zip"):
    print(f"--- {filename} ---")
    for item in items:
        print(item)

# Load using a custom request with headers
req = urllib.request.Request("https://example.com/archive.zip", headers={"Accept": "application/zip"})
for filename, items in jsonl.load_archive(req):
    print(f"--- {filename} ---")
    for item in items:
        print(item)
```

### Filter files with pattern matching

Use Unix shell-style wildcards to select specific files within the archive:

| Pattern            | Matches                                   |
|--------------------|-------------------------------------------|
| `*.jsonl`          | All `.jsonl` files (default)              |
| `users*.jsonl`     | Files starting with `users`               |
| `data/[ab]*.jsonl` | Files in `data/` starting with `a` or `b` |
| `*`                | All files                                 |

For more details, see the [fnmatch documentation](https://docs.python.org/3/library/fnmatch.html).

```python
import jsonl

# Load only files matching a specific pattern
for filename, items in jsonl.load_archive("archive.zip", pattern="users*.jsonl"):
    print(f"--- {filename} ---")
    for item in items:
        print(item)
```
