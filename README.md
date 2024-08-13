# jsonl

[![CI](https://github.com/rmoralespp/jsonl/workflows/CI/badge.svg)](https://github.com/rmoralespp/jsonl/actions?query=event%3Arelease+workflow%3ACI)
[![pypi](https://img.shields.io/pypi/v/jsonl.svg)](https://pypi.python.org/pypi/jsonl-py)
[![versions](https://img.shields.io/pypi/pyversions/jsonl.svg)](https://github.com/rmoralespp/jsonl)
[![codecov](https://codecov.io/gh/rmoralespp/jsonl/branch/main/graph/badge.svg)](https://app.codecov.io/gh/rmoralespp/jsonl)
[![license](https://img.shields.io/github/license/rmoralespp/jsonl.svg)](https://github.com/rmoralespp/jsonl/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: ruff](https://img.shields.io/badge/linter-_ruff-orange)](https://github.com/charliermarsh/ruff)

### About

jsonl is a Python Library for Handling JSON Lines Files

`jsonl` exposes an API similar to the `json` module from the standard library.

### Installation (via pip)

```pip install jsonl```

### Tests

```
(env)$ pip install -r requirements.txt   # Ignore this command if it has already been executed
(env)$ pytest tests/
(env)$ pytest --cov jsonl # Tests with coverge
```

### Usage

#####  dumps
```
dumps(iterable, **kwargs)

Serialize iterable to a JSON lines formatted string.

:param Iterable[Any] iterable: Iterable of objects
:param kwargs: `json.dumps` kwargs
:rtype: str
```

#####  dump
```
dump(iterable, fp, **kwargs)

Serialize iterable as a JSON lines formatted stream to file-like object.

:param Iterable[Any] iterable: Iterable of objects
:param fp: file-like object
:param kwargs: `json.dumps` kwargs

Example:
    import jsonl.dump

    data = ({'foo': 1}, {'bar': 2})
    with open('myfile.jsonl', mode='w', encoding='utf-8') as file:
        jsonl.dump(data, file)
```


#####  dump_into
```
dump_into(filename, iterable, encoding=utf_8, **kwargs)

Dump iterable to a JSON lines file.

Example:
    import jsonl.dump_into

    data = ({'foo': 1}, {'bar': 2})
    jsonl.dump_into("myfile.jsonl", data)
```

#####  dump_fork
```
dump_fork(iterable_by_path, encoding=utf_8, dump_if_empty=True, **kwargs)

Incrementally dumps different groups of elements into
the indicated JSON lines file.
***Useful to reduce memory consumption***

:param Iterable[file_path, Iterable[dict]] iterable_by_path: Group items by file path
:param encoding: file encoding. 'utf-8' used by default
:param bool dump_if_empty: If false, don't create an empty JSON lines file.
:param kwargs: `json.dumps` kwargs

Examples:
    import jsonl.dump_fork

    path_items = (
        ("num.jsonl", ({"value": 1}, {"value": 2})),
        ("num.jsonl", ({"value": 3},)),
        ("foo.jsonl", ({"a": "1"}, {"b": 2})),
        ("baz.jsonl", ()),
    )
    jsonl.dump_fork(path_items)
```

#####  load
```
load(fp, **kwargs)

Deserialize a file-like object containing JSON Lines into a Python iterable of objects.

:param fp: file-like object
:param kwargs: `json.loads` kwargs
:rtype: Iterable[Any]
```

#####  load_from
```
def load_from(filename, encoding=utf_8, **kwargs)
 
Deserialize a JSON Lines file into a Python iterable of objects.

:param filename: path
:param encoding: file encoding. 'utf-8' used by default
:param kwargs: `json.loads` kwargs
:rtype: Iterable[str]

Examples:
    import jsonl.load_from

    it = jsonl.load_from("myfile.jsonl")
    next(it)

```