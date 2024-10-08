# Dump an iterable to a JSON Lines file incrementally.

Dump JSON Lines (jsonl) files incrementally, supporting both uncompressed and compressed formats and allowing
custom serialization and opener callbacks.

#### Dump the data to an uncompressed file at the specified path.

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "file.jsonl")
```

#### Dump the data to a compressed file at the specified path.

!!! note
    Supported compression formats are: **gzip (.gz), bzip2 (.bz2), xz (.xz)**
    If a file extension is not provided or is unrecognized, the file will be assumed to be uncompressed.

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Dump to a gzip compressed file.
jsonl.dump(data, "file.jsonl.gz")

# Dump to a bzip2 compressed file.
jsonl.dump(data, "file.jsonl.bz2")

# Dump to a xz compressed file.
jsonl.dump(data, "file.jsonl.xz")

# Dump to a text file because the extension is not recognized.
jsonl.dump(data, "file.jsonl.foo")
```

#### Dump the data to the already opened compressed file.

```python
import gzip
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Dump to an opened gzip file, text_mode is false because it is a binary file.
with gzip.open("file.jsonl.gz", mode="wb") as fp:
    jsonl.dump(data, fp, text_mode=False)
```

#### Append the data to the end of the existing compressed file.

```python

import gzip
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Text mode is false because it is a binary file.
with gzip.open("file.jsonl.gz", mode="ab") as fp:
    jsonl.dump(data, fp, text_mode=False)
```

#### Dump the data to a custom file object.

!!! tip
    Use this feature when you need to write the data to a custom file object.
    The custom file object must have a `write` or `writelines` method.

```python

import jsonl


class MyCustomFile1:
    """A custom file object that has a write method."""

    def write(self, line):
        print(line)


class MyCustomFile2:
    """A custom file object that has a writelines method."""

    def writelines(self, lines):
        print("".join(lines))


data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Dump the data to the custom file object using the write method.
jsonl.dump(data, MyCustomFile1(), text_mode=True)

# Dump the data to the custom file object using the writelines method.
jsonl.dump(data, MyCustomFile2(), text_mode=True)
```

#### Dump data with a custom serialization.

The `json_dumps` parameter allows for custom serialization and must take a Python object and return a
JSON-formatted string.

The following example shows how to use the `json_dumps` parameter to serialize data with the `orjson` and `ujson `
libraries. Make sure to install these libraries to run the example.

```console
pip install orjson ujson # Ignore this command if these libraries are already installed.
```

```python

import orjson
import ujson

import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Dump the data using the ujson library.
jsonl.dump(data, "foo.jsonl", json_dumps=ujson.dumps, ensure_ascii=False)

# Dump the data using the orjson library.
jsonl.dump(data, "var.jsonl", json_dumps=orjson.dumps)
```
