# jsonl.open_stream

Open a local path, URL, or binary file-like object as a readable binary stream with transparent
compression handling.

```python
jsonl.open_stream(source, *, opener=None)
```

The context manager detects gzip, bzip2, xz, and zstandard compression from the path or stream
signature. It provides a common streaming interface for consumers that need to process data
incrementally without loading the complete resource into memory. The returned stream can be passed
to a parser, copied to another destination, hashed, inspected line by line, or processed with any
other binary-stream API.

Paths and URLs are opened and closed by the context manager. A file-like object supplied by the
caller remains open.

```python
import jsonl

with jsonl.open_stream("records.jsonl.gz") as stream:
    for line in stream:
        print(line.decode("utf-8").rstrip())
```

For applications that use an incremental parser, the same stream can be handed off to that parser:

```python
import ijson
import jsonl

with jsonl.open_stream("records.json.gz") as stream:
    for item in ijson.items(stream, "item"):
        process(item)
```

`open_stream()` does not interpret the content and does not open ZIP/TAR archives. Use
`load()` for JSON Lines records, or `load_archive()` for archives containing multiple members.
