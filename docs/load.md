# jsonl.load

Deserialize a JSON Lines source into an iterator of Python objects. Supports filenames, URLs,
`urllib.request.Request` objects, and file-like objects.

## Function Signature

```python
jsonl.load(
    source,
    *,
    opener=None,
    broken=False,
    json_loads=None,
    **json_loads_kwargs,
)
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `source` | `str`, `PathLike`, `URL`, `Request`, file-like | *(required)* | The JSON Lines source to read from |
| `opener` | `Callable` or `None` | `None` | Custom function to open the file (not supported for URLs) |
| `broken` | `bool` | `False` | If `True`, skip malformed lines and log a warning instead of raising an exception |
| `json_loads` | `Callable` or `None` | `None` | Custom deserialization function. Defaults to `json.loads` |
| `**json_loads_kwargs` | | | Additional keyword arguments passed to the deserialization function |

### Returns

`Iterator[Any]` — An iterator yielding deserialized Python objects, one per line.

### Compression Detection

<a id="note-compression"></a>
!!! note
    Supported compression formats: **gzip (.gz), bzip2 (.bz2), xz (.xz)**

    The compression format is resolved using two strategies:

    1. **By file extension** — if the file has a recognized extension (`.gz`, `.bz2`, `.xz`), that format is used directly.
    2. **By magic numbers** — when the extension is not recognized, **jsonl** inspects the first bytes of the file
       ([magic numbers](https://en.wikipedia.org/wiki/List_of_file_signatures)) to auto-detect the compression format.

    If neither method identifies a known format, the file is treated as uncompressed.

---

## Examples

### Load from a file path

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "file.jsonl")

for item in jsonl.load("file.jsonl"):
    print(item)
```

### Load from a compressed file

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Write to a gzip-compressed file
jsonl.dump(data, "file.jsonl.gz")

# Load automatically detects the compression format
for item in jsonl.load("file.jsonl.gz"):
    print(item)
```

### Load from an open file object

!!! tip
    Useful when you need to read from a custom source or control how the file is opened.

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "file.jsonl")

with open("file.jsonl") as fp:
    for item in jsonl.load(fp):
        print(item)
```

### Load from a URL

You can load JSON Lines directly from a remote URL. For custom request headers, use `urllib.request.Request`:

```python
import urllib.request
import jsonl

# Load directly from a URL
for item in jsonl.load("https://example.com/file.jsonl"):
    print(item)

# Load using a custom request with headers
req = urllib.request.Request(
    "https://example.com/file.jsonl",
    headers={"Accept": "application/jsonl"},
)
for item in jsonl.load(req):
    print(item)
```

### Handle broken lines

!!! warning
    When `broken=False` (the default), an exception is raised on the first malformed line.
    When `broken=True`, malformed lines are skipped and a warning is logged.

```python
import jsonl

# Create a file with a broken JSON line
with open("file.jsonl", mode="wt", encoding="utf-8") as fp:
    fp.write('{"name": "Gilbert"}\n')
    fp.write('{"name": "May", "wins": []\n')  # Missing closing brace
    fp.write('{"name": "Richard"}\n')

# Skip broken lines
for item in jsonl.load("file.jsonl", broken=True):
    print(item)
```

*Output:*

```text
WARNING:jsonl:Broken line at 2: Expecting ',' delimiter: line 2 column 1 (char 28)
{'name': 'Gilbert'}
{'name': 'Richard'}
```

### Custom deserialization

#### Using a third-party library

[`orjson`](https://github.com/ijl/orjson) is a popular high-performance JSON library:

```python
import orjson
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "file.jsonl")

for item in jsonl.load("file.jsonl", json_loads=orjson.loads):
    print(item)
```

#### Passing additional keyword arguments

Extra keyword arguments are forwarded to the deserialization function (by default, `json.loads`).
For example, parse float values as `decimal.Decimal`:

```python
import decimal
import jsonl

data = [
    {"name": "Gilbert", "wins_avg": 2.5},
    {"name": "May", "wins_avg": 3.75},
]

jsonl.dump(data, "file.jsonl")

for item in jsonl.load("file.jsonl", parse_float=decimal.Decimal):
    print(item)
    # float values are now decimal.Decimal instances
```

### Custom opener

The `opener` parameter lets you control how the file is opened. For example, reading from a ZIP archive:

```python
import zipfile
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Create a ZIP archive containing a jsonl file
jsonl.dump(data, "file.jsonl")
with zipfile.ZipFile("data.zip", "w") as zf:
    zf.write("file.jsonl")


def opener(name, *args, **kwargs):
    return zipfile.ZipFile(name).open("file.jsonl")


for item in jsonl.load("data.zip", opener=opener):
    print(item)
```
