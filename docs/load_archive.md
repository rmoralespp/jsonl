# Load JSON Lines Files from an Archive (ZIP or TAR)

Allows to load JSON Lines **(.jsonl)** files from a **ZIP** or **TAR** archive.

- Support compressed TAR archives (e.g., `.tar.gz`, `.tar.bz2`, `.tar.xz`).
- Support ZIP archives with password protection.
- Filename filtering using Unix shell-style wildcards via `fnmatch`. Use a pattern (e.g., *.jsonl) to selectively load
  only matching files within the archive.
- Support for both compressed and uncompressed `.jsonl` files inside the archive. (e.g., `*.jsonl.gz` or `*.jsonl.bz2`
  or `*.jsonl.xz`).
- Graceful handling of malformed or broken lines.
- Optional custom deserialization and opener callbacks for advanced use cases.


**Example usage:**

```python
import jsonl

path = "path/to/archive.zip"  # or "path/to/archive.tar.gz"
# Load all JSON Lines files matching the pattern "*.jsonl" from the archive
for filename, items in jsonl.load_archive(path):
    print("Filename:", filename)
    print("Data:", tuple(items))
```

## ZIP password protection

`load_archive` can read password-protected ZIP archives. To do so, you need to provide a `password` argument:

```python
import jsonl

path = "path/to/protected.zip"
for filename, items in jsonl.load_archive(path, password="your_password"):
    print("Filename:", filename)
    print("Data:", tuple(items))
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
for filename, items in jsonl.load_archive(path, pattern="myfile*.jsonl"):
    print("Filename:", filename)
    print("Data:", tuple(items))
```