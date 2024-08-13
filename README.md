# jsonl

[![CI](https://github.com/rmoralespp/jsonl/workflows/CI/badge.svg)](https://github.com/rmoralespp/jsonl/actions?query=event%3Arelease+workflow%3ACI)
[![pypi](https://img.shields.io/pypi/v/py-jsonl.svg)](https://pypi.python.org/pypi/py-jsonl)
[![versions](https://img.shields.io/pypi/pyversions/py-jsonl.svg)](https://github.com/rmoralespp/jsonl)
[![codecov](https://codecov.io/gh/rmoralespp/jsonl/branch/main/graph/badge.svg)](https://app.codecov.io/gh/rmoralespp/jsonl)
[![license](https://img.shields.io/github/license/rmoralespp/jsonl.svg)](https://github.com/rmoralespp/jsonl/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: ruff](https://img.shields.io/badge/linter-_ruff-orange)](https://github.com/charliermarsh/ruff)

### About

jsonl is a simple Python Library for Handling JSON Lines Files

`jsonl` exposes an API similar to the `json` module from the standard library.

### Installation (via pip)

```pip install py-jsonl```


### Usage

#####  dumps
```
dumps(iterable, **kwargs)

Serialize an iterable into a JSON Lines formatted string.

:param Iterable[Any] iterable: Iterable of objects
:param kwargs: `json.dumps` kwargs
:rtype: str

Examples:
    import jsonl.dumps

    data = ({'foo': 1}, {'bar': 2})
    result = jsonl.dumps(data, file)
    print(result)  # >> '{"foo": 1}\n{"bar": 2}\n'
```

#####  dump
```
dump(iterable, fp, **kwargs)

Serialize an iterable as a JSON Lines formatted stream to a file-like object.

:param Iterable[Any] iterable: Iterable of objects
:param fp: file-like object
:param kwargs: `json.dumps` kwargs

Examples:
    import jsonl.dump

    data = ({'foo': 1}, {'bar': 2})
    with open('myfile.jsonl', mode='w', encoding='utf-8') as file:
        jsonl.dump(data, file)
```


#####  dump_into
```
dump_into(filename, iterable, encoding="utf-8", **kwargs)

Dump an iterable to a JSON Lines file.

Examples:
    import jsonl.dump_into

    data = ({'foo': 1}, {'bar': 2})
    jsonl.dump_into("myfile.jsonl", data)
```

#####  dump_fork
```
dump_fork(path_iterables, encoding="utf-8", dump_if_empty=True, **kwargs)

Incrementally dumps multiple iterables into the specified JSON Lines files, 
effectively reducing memory consumption.

:param Iterable[str, Iterable[Any]] path_iterables: Iterable of iterables by filepath
:param encoding: file encoding. 'utf-8' used by default
:param bool dump_if_empty: If false, don't create an empty JSON lines file.
:param kwargs: `json.dumps` kwargs

Examples:
    import jsonl.dump_fork

    path_iterables = (
        ("num.jsonl", ({"value": 1}, {"value": 2})),
        ("num.jsonl", ({"value": 3},)),
        ("foo.jsonl", ({"a": "1"}, {"b": 2})),
        ("baz.jsonl", ()),
    )
    jsonl.dump_fork(path_iterables)
```

#####  load
```
load(fp, **kwargs)

Deserialize a file-like object containing JSON Lines into a Python iterable of objects.

:param fp: file-like object
:param kwargs: `json.loads` kwargs
:rtype: Iterable[Any]

Examples:
    import io
    import jsonl.load
    
    iterable = jsonl.load(io.StringIO('{"foo": 1}\n{"ño": 2}\n'))
    print(tuple(iterable))  # >> ({"foo": 1}, {"ño": 2})
```

#####  load_from
```
def load_from(filename, encoding=utf_8, **kwargs)
 
Deserialize a JSON Lines file into an iterable of Python objects.

:param filename: file path
:param encoding: file encoding. 'utf-8' used by default
:param kwargs: `json.loads` kwargs
:rtype: Iterable[str]

Examples:
    import jsonl.load_from

    iterable = jsonl.load_from("myfile.jsonl")
    print(tuple(iterable))
```

### Unit tests

```
(env)$ pip install -r requirements.txt   # Ignore this command if it has already been executed
(env)$ pytest tests/
(env)$ pytest --cov jsonl # Tests with coverge
```