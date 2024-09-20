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

Features:

- Offers an API similar to Python's built-in `json` module.
- Supports serialization/deserialization using the most common `json` libraries, prioritizing `orjson`, then `ujson`,
  and defaulting to the standard `json` if the others are unavailable.
- Enables compression using `gzip`, `bzip2`, and `xz` formats.

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

jsonl.dump(data, "file.jsonl")  # as list
jsonl.dump(iter(data), "file.jsonl")  # as iterable
```

Write the data to a compressed file at the specified path.

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "file.jsonl.gz")
jsonl.dump(data, "file.jsonl.bz2")
jsonl.dump(data, "file.jsonl.xz")
```

Write the data to the already opened gzipped file.

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

Append the data to the end of the existing gzipped file.

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

##### Dump fork (Incremental dump)

Incrementally dumps multiple iterables into the specified jsonlines file paths,
effectively reducing memory consumption.

**Examples:**

```python
import jsonl

path_iterables = (
    ("num.jsonl", ({"value": 1}, {"value": 2})),
    ("foo.jsonl", ({"a": "1"}, {"b": 2})),
    ("num.jsonl", ({"value": 3},)),
    ("foo.jsonl", ()),
)
jsonl.dump_fork(path_iterables)
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

### Unit tests

```
(env)$ pip install -r requirements.txt   # Ignore this command if it has already been executed
(env)$ pytest tests/
(env)$ pytest --cov jsonl # Tests with coverge
```
