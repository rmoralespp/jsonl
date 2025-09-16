# Load multiple JSON Lines Files from an Archive (ZIP or TAR) incrementally

Allows to load multiple JSON Lines **(.jsonl)** files incrementally from a **ZIP** or **TAR** archive.

- Support compressed TAR archives (e.g., `.tar.gz`, `.tar.bz2`, `.tar.xz`).
- Support loading the archive from a URL.
- Support ZIP archives with password protection.
- Filename filtering using Unix shell-style wildcards via `fnmatch`. Use a pattern (e.g., *.jsonl) to selectively load
  only matching files within the archive.
- Support for both compressed and uncompressed `.jsonl` files inside the archive. (e.g., `*.jsonl.gz` or `*.jsonl.bz2`
  or `*.jsonl.xz` **(Check [note](load.md#note-compression) for more details)**.
- Graceful handling of malformed or broken lines.
- Optional custom deserialization and opener callbacks for advanced use cases.


**Load from a local archive**

```python
import jsonl

path = "path/to/archive.zip"
# Load all JSON Lines files matching the pattern "*.jsonl"
for filename, iterator in jsonl.load_archive(path):
    print("Filename:", filename)
    print("Data:", tuple(iterator))
```

**Load from a remote archive (URL)**

You can load the archive from a URL, if needed you can also create custom requests using `urllib.request.Request`.

```python
import urllib.request

import jsonl

# Load all JSON Lines files matching the pattern "*.jsonl" from a remote archive:
# ------------------------

# Load directly from a URL
for filename, iterator in jsonl.load_archive("https://example.com/archive.zip"):
    print("Filename:", filename)
    print("Data:", tuple(iterator))

    
# Load using a custom request
req = urllib.request.Request("https://example.com/archive.zip", headers={"Accept": "application/zip"})
for filename, iterator in jsonl.load_archive(req):
    print("Filename:", filename)
    print("Data:", tuple(iterator))
```

## Pattern matching

You can use Unix shell-style wildcards to filter files in the archive. The `pattern` argument supports:

- `*` matches everything
- `?` matches a single character
- `[seq]` matches any character in `seq`
- `[!seq]` matches any character not in `seq`

For more information, refer to the [fnmatch documentation](https://docs.python.org/es/3.12/library/fnmatch.html).


```python
import jsonl

path = "path/to/archive.zip"
# Load all JSON Lines files matching the pattern "myfile*.jsonl" from the archive
for filename, iterator in jsonl.load_archive(path, pattern="myfile*.jsonl"):
    print("Filename:", filename)
    print("Data:", tuple(iterator))
```
