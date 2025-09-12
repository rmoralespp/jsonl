# Dump multiple JSON Lines Files into an Archive (ZIP or TAR) incrementally

- Support ZIP or TAR archives, including compressed TAR archives (e.g., `.tar.gz`, `.tar.bz2`, `.tar.xz`).
- Support for both compressed and uncompressed `.jsonl` files inside the archive. (e.g., `*.jsonl.gz` or `*.jsonl.bz2`
  or `*.jsonl.xz`).
- Optional custom serialization and opener callbacks for advanced use cases.

!!! warning
    If the given archive already exists on the given path, it will be overwritten.

!!! note
    - Paths provided in the `data` argument must be relative. Absolute paths are not allowed and will raise an error.
    - If `data` contains multiple items for the same path, they will be appended to the corresponding file within the archive.

**Example usage:**

```python
import jsonl

data = [
    # this will create a new file1.jsonl in the archive
    ("file1.jsonl", [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]),
    # this will create a new file1.jsonl.gz in the archive
    ("path/to/file2.jsonl.gz", [{"name": "Charlie", "age": 35}, {"name": "David", "age": 40}]),
    # this will append to the file1.jsonl
    ("file1.jsonl", [{"name": "Eve", "age": 28}]),
]
jsonl.dump_archive("my_archive.zip", data)
```
