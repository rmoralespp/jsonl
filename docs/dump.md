##### Dump an iterable to a JSON Lines file. (dump)

**Examples:**

Write the data to an uncompressed file at the specified path.

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "file.jsonl")
```

Write the data to a compressed file at the specified path.

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "file.jsonl.gz")  # gzip compression
jsonl.dump(data, "file.jsonl.bz2")  # bzip2 compression
jsonl.dump(data, "file.jsonl.xz")  # xz compression
```

Write the data to the already opened compressed file.

```python
import gzip
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

with gzip.open("file.jsonl.gz", mode="wb") as fp:
    jsonl.dump(data, fp, text_mode=False)
```

Append the data to the end of the existing compressed file.

```python

import gzip
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

with gzip.open("file.jsonl.gz", mode="ab") as fp:
    jsonl.dump(data, fp, text_mode=False)
```

Write the data to a custom file object.

```python

import jsonl


class MyCustomFile1:

    def write(self, line):
        print(line)


class MyCustomFile2:

    def writelines(self, lines):
        print("".join(lines))


data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, MyCustomFile1(), text_mode=True)
jsonl.dump(data, MyCustomFile2(), text_mode=True)
```

Write the data using a custom serialization callback.

`pip install orjson ujson`  # Ignore this command if these libraries are already installed.

```python

import orjson
import ujson

import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "foo.jsonl", json_dumps=ujson.dumps, ensure_ascii=False) # using (ujson)
jsonl.dump(data, "var.jsonl", json_dumps=orjson.dumps) # using (orjson)
```
