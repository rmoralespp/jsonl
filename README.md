# jsonl

[![CI](https://github.com/rmoralespp/jsonl/workflows/CI/badge.svg)](https://github.com/rmoralespp/jsonl/actions?query=event%3Arelease+workflow%3ACI)
[![pypi](https://img.shields.io/pypi/v/py-jsonl.svg)](https://pypi.python.org/pypi/py-jsonl)
[![versions](https://img.shields.io/pypi/pyversions/py-jsonl.svg)](https://github.com/rmoralespp/jsonl)
[![codecov](https://codecov.io/gh/rmoralespp/jsonl/branch/main/graph/badge.svg)](https://app.codecov.io/gh/rmoralespp/jsonl)
[![license](https://img.shields.io/github/license/rmoralespp/jsonl.svg)](https://github.com/rmoralespp/jsonl/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: ruff](https://img.shields.io/badge/linter-_ruff-orange)](https://github.com/charliermarsh/ruff)

### About

Useful functions for working with jsonlines data as described: https://jsonlines.org/

**Features:**

- 🌎 Offers an API similar to Python's standard `json` module.
- 🚀 Supports custom serialization/deserialization callbacks. By default, it uses the standard `json` module.
- 🗜️ Enables compression using `gzip`, `bzip2`, and `xz` formats.
- 🔧 Load files containing broken lines, skipping any malformed lines.
- 📦 Provides a simple API for incremental writing to multiple files.

### Installation (via pip)

```pip install py-jsonl```

### Usage

##### Serialize an iterable into a JSON Lines formatted string. (dumps)

Examples:

```python
import jsonl

data = ({'foo': 1}, {'bar': 2})
result = jsonl.dumps(data)
print(result)
```

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

##### Dump fork (Incremental dump)

Incrementally dumps multiple iterables into the specified jsonlines file paths,
effectively reducing memory consumption.

**Examples:**

`pip install orjson ujson`  # Ignore this command if these libraries are already installed.

```python
import orjson
import ujson
import jsonl


def worker():
    yield ("num.jsonl", ({"value": 1}, {"value": 2}))
    yield ("foo.jsonl", iter(({"a": "1"}, {"b": 2})))
    yield ("num.jsonl", [{"value": 3}])
    yield ("foo.jsonl", ())


jsonl.dump_fork(worker())  # using (json)
jsonl.dump_fork(worker(), json_dumps=ujson.dumps, ensure_ascii=False)  # using (ujson)
jsonl.dump_fork(worker(), json_dumps=orjson.dumps)  # using (orjson)
```

##### load

Deserialize a UTF-8 encoded jsonlines file into an iterable of Python objects.

**Examples:**

Load an uncompressed file from the specified path.

```python
import jsonl

path = "file.jsonl"
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, path)
iterable = jsonl.load(path)
print(tuple(iterable))
```

Load a compressed file from the specified path.

```python
import jsonl

path = "file.jsonl.gz"
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, path)
iterable = jsonl.load(path)
print(tuple(iterable))
```

Load a compressed file from the specified open file object.

```python
import gzip
import jsonl

path = "file.jsonl.gz"
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, path)
with gzip.open(path, mode="rb") as fp:
    iterable = jsonl.load(fp)
    print(tuple(iterable))
```

Load a file containing broken lines, skipping any malformed lines.

```python
import jsonl

with open("file.jsonl", mode="wt", encoding="utf-8") as fp:
    fp.write('{"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]}\n')
    fp.write('{"name": "May", "wins": []\n')  # missing closing bracket
    fp.write('{"name": "Richard", "wins": []}\n')

iterable = jsonl.load("file.jsonl", broken=True)
print(tuple(iterable))
```

Load a file using a custom deserialization callback.

`pip install orjson ujson`  # Ignore this command if these libraries are already installed.

```python
import orjson
import ujson
import jsonl

path = "file.jsonl"
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, path)

iterable1 = jsonl.load(path, json_loads=ujson.loads)  # using (ujson)
iterable2 = jsonl.load(path, json_loads=orjson.loads)  # using (orjson)
print(tuple(iterable1))
print(tuple(iterable2))
```

### Unit tests

```
(env)$ pip install -r requirements-dev.txt   # Ignore this command if it has already been executed
(env)$ pytest tests/
(env)$ pytest --cov jsonl # Tests with coverge
```


### Documentation

```
(env)$ pip install -r requirements-docs.txt   # Ignore this command if it has already been executed
(env)$ mkdocs serve # Start the live-reloading docs server
(env)$ mkdocs build # Build the documentation site
```
