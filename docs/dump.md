# Dump an iterable to a JSON Lines file incrementally.

Dump JSON Lines **(jsonl)** files incrementally, supporting both uncompressed and compressed formats and allowing
custom serialization and opener callbacks.

#### Dump the data to an uncompressed file at the specified path

```python
# -*- coding: utf-8 -*-

import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "file.jsonl")
```

#### Dump the data to a compressed file at the specified path

!!! note
    Supported compression formats are: **gzip (.gz), bzip2 (.bz2), xz (.xz)**
    If a file extension is not provided or is unrecognized, the file will be assumed to be uncompressed.

```python
# -*- coding: utf-8 -*-

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

#### Dump the data to the already opened file

```python
# -*- coding: utf-8 -*-

import gzip

import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Dump to an opened file, Text mode is True because it is a text file.
with open("file.jsonl", mode="wt", encoding="utf-8") as fd:
    jsonl.dump(data, fd, text_mode=True)

# Dump to an opened gzip file, Text mode is false because it is a binary file.
with gzip.open("file.jsonl.gz", mode="wb") as fd:
    jsonl.dump(data, fd, text_mode=False)
```

#### Append the data to the end of the existing file

```python
# -*- coding: utf-8 -*-

import gzip

import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Compressed file: Text mode is false because it is a binary file.
with gzip.open("file.jsonl.gz", mode="ab") as fp:
    jsonl.dump(data, fp, text_mode=False)

# Uncompressed file: Text mode is true because it is a text file.
with open("file.jsonl", mode="at", encoding="utf-8") as fp:
    jsonl.dump(data, fp, text_mode=True)
```

#### Dump the data to a custom file object

!!! tip
    Use this feature when you need to write the data to a custom file object.
    The custom file object must have a `write` or `writelines` method.

```python
# -*- coding: utf-8 -*-

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

#### Dump data with a custom serialization

##### Passing a `json_dumps` function

The `json_dumps` parameter allows for custom serialization and must take a Python object and return a
JSON-formatted string.

The following example shows how to use the `json_dumps` parameter to serialize data with the `orjson` and `ujson `
libraries. Make sure to install these libraries to run the example.

```bash
pip install orjson ujson # Ignore this command if these libraries are already installed.
```

```python
# -*- coding: utf-8 -*-

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

##### Passing additional keyword arguments

The  `jsonl.dump` function accepts additional keyword arguments that are passed directly to the underlying
serialization function (by default, `json.dumps`). This allows for customization of the serialization process,
such as controlling indentation, sorting keys, or handling special data types.

Here’s an example that demonstrates how to use additional keyword arguments to customize the JSON serialization:

```python
# -*- coding: utf-8 -*-

import json

import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]
# Dump the data with compact separators to minimize file size.
jsonl.dump(data, "compact.jsonl", separators=(',', ':'))
```