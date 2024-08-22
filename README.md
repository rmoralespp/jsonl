# jsonl

[![CI](https://github.com/rmoralespp/jsonl/workflows/CI/badge.svg)](https://github.com/rmoralespp/jsonl/actions?query=event%3Arelease+workflow%3ACI)
[![pypi](https://img.shields.io/pypi/v/py-jsonl.svg)](https://pypi.python.org/pypi/py-jsonl)
[![versions](https://img.shields.io/pypi/pyversions/py-jsonl.svg)](https://github.com/rmoralespp/jsonl)
[![codecov](https://codecov.io/gh/rmoralespp/jsonl/branch/main/graph/badge.svg)](https://app.codecov.io/gh/rmoralespp/jsonl)
[![license](https://img.shields.io/github/license/rmoralespp/jsonl.svg)](https://github.com/rmoralespp/jsonl/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: ruff](https://img.shields.io/badge/linter-_ruff-orange)](https://github.com/charliermarsh/ruff)

### About

Useful functions for working with jsonlines data as
described: https://jsonlines.org/

Features:

- Exposes an API similar to the `json` module from the standard library.
- Supports `orjson`, `ujson` libraries or standard `json` for serialization/deserialization, prioritizing `orjson`,
  then `ujson`, and defaulting to the standard `json` if none are installed.
- Supports `gzip` and `bzip2` compression formats.

### Installation (via pip)

```pip install py-jsonl```

### `jsonl.py` module Usage

##### dumps

Serialize an iterable into a jsonlines formatted string.

```
dumps(iterable, **kwargs)

:param Iterable[Any] iterable: Iterable of objects
:param kwargs: `json.dumps` kwargs
:rtype: str
```

Examples:

```python
import jsonl

data = ({'foo': 1}, {'bar': 2})
result = jsonl.dumps(data)
print(result)  # >> '{"foo": 1}\n{"bar": 2}\n'
```

##### dump

Dump an iterable to a jsonlines file.
- Use (`.gz`, `.gzip`, `.bz2`) extensions to dump the compressed file.
- Dumps falls back to the following functions: (`orjson.dumps`, `ujson.dumps`, and `json.dumps`).

```
dump(iterable, file, **kwargs)

:param Iterable[Any] iterable: Iterable of objects
:param Union[str | bytes | os.PathLike | io.IOBase] file: File to dump
:param kwargs: `json.dumps` kwargs
```

Examples:

```python
import gzip

import jsonl

data = ({'foo': 1}, {'bar': 2})

# Dump the data into an uncompressed file at the given path.
jsonl.dump(data, "file1.jsonl")

# Dump the data into a gzipped file at the given path.
jsonl.dump(data, "file2.jsonl.gz")

# Dump the data into the already opened gzipped file.
with gzip.open("file3.jsonl.gz", mode="wb") as fp:
    jsonl.dump(data, fp)

# Append the data to the end of the existing gzipped file.
with gzip.open("file3.jsonl.gz", mode="ab") as fp:
    jsonl.dump(data, fp)
```

##### dump_fork

Incrementally dumps multiple iterables into the specified jsonlines file paths,
effectively reducing memory consumption.

- Use (`.gz`, `.gzip`, `.bz2`) extensions to dump the compressed file.
- Dumps falls back to the following functions: (`orjson.dumps`, `ujson.dumps`, and `json.dumps`).

```
dump_fork(path_iterables, dump_if_empty=True, **kwargs)

:param Iterable[str, Iterable[Any]] path_iterables: Iterable of iterables by filepath
:param bool dump_if_empty: If false, don't create an empty jsonlines file.
:param kwargs: `json.dumps` kwargs
```

Examples:

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

Deserialize a UTF-8-encoded jsonlines file into an iterable of Python objects.

- Recognizes (`.gz`, `.gzip`, `.bz2`)  extensions to load compressed files.
- Loads falls back to the following functions: (`orjson.loads`, `ujson.loads`, and `json.loads`).

```
def load(file, **kwargs)

:param Union[str | bytes | os.PathLike | io.IOBase] file: File to load
:param kwargs: `json.loads` kwargs
:rtype: Iterable[Any]
```

Examples:

```python
import gzip

import jsonl

# Load the uncompressed file from the given path.
iterable1 = jsonl.load("file1.jsonl")
print(tuple(iterable1))

# Load the gzipped file from the given path.
iterable2 = jsonl.load("file2.jsonl.gz")
print(tuple(iterable2))

# Load the gzipped file from the given open file.
with gzip.open("file3.jsonl.gz", mode="rb") as fp:
    iterable3 = jsonl.load(fp)
    print(tuple(iterable3))
```

### `flask_jsonl.py` module Usage

```


```

### Unit tests

```
(env)$ pip install -r requirements.txt   # Ignore this command if it has already been executed
(env)$ pytest tests/
(env)$ pytest --cov jsonl # Tests with coverge
```
