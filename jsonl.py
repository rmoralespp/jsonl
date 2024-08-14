# -*- coding: utf-8 -*-

"""
Useful functions for working with JSON lines data as
described: https://jsonlines.org/

`jsonl` exposes an API similar to the `json` module from the standard library.

Recognizes ".gz" and ".gzip" extensions to handle gzip-compressed JSON line files.
"""

__version__ = "1.0.5"
__all__ = [
    "dump",
    "dumps",
    "dump_into",
    "dump_fork",
    "load",
    "load",
    "load_from",
]
__title__ = "py-jsonl"

import functools
import gzip
import json
import os

empty = object()
dumps_line = functools.partial(json.dumps, ensure_ascii=False)
utf_8 = "utf-8"
new_line = "\n"


def open_file(name, mode="rt", encoding=utf_8):
    """Open file depending on file extension."""

    opener = gzip.open if name.endswith((".gz", ".gzip")) else open
    return opener(name, mode=mode, encoding=encoding)


def dumper(iterable, **kwargs):
    """Generator yielding JSON lines."""

    encode = functools.partial(dumps_line, **kwargs)
    for obj in iter(iterable):
        yield encode(obj)
        yield new_line


def dumps(iterable, **kwargs):
    """
    Serialize an iterable into a JSON Lines formatted string.

    :param Iterable[Any] iterable: Iterable of objects
    :param kwargs: `json.dumps` kwargs
    :rtype: str

    Examples:
        import jsonl

        data = ({'foo': 1}, {'bar': 2})
        result = jsonl.dumps(data)
        print(result)  # >> '{"foo": 1}\n{"bar": 2}\n'
    """

    return "".join(dumper(iterable, **kwargs))


def dump(iterable, fp, **kwargs):
    """
    Serialize an iterable as a JSON Lines formatted stream to a file-like object.

    :param Iterable[Any] iterable: Iterable of objects
    :param fp: file-like object
    :param kwargs: `json.dumps` kwargs

    Examples:
        import jsonl

        data = ({'foo': 1}, {'bar': 2})
        with open('myfile.jsonl', mode='w', encoding='utf-8') as file:
            jsonl.dump(data, file)
    """

    fp.writelines(dumper(iterable, **kwargs))


def dump_into(filename, iterable, **kwargs):
    """
    Dump an iterable to a JSON Lines file.
    Use ".gz" or ".gzip" extensions to dump the gzipped file.

    Example:
        import jsonl

        data = ({'foo': 1}, {'bar': 2})

        jsonl.dump_into("myfile.jsonl", data)     # file
        jsonl.dump_into("myfile.jsonl.gz", data)  # gzipped file
    """

    with open_file(filename, mode="wt", encoding=utf_8) as f:
        dump(iterable, f, **kwargs)


def dump_fork(path_iterables, dump_if_empty=True, **kwargs):
    """
    Incrementally dumps multiple iterables into the specified JSON Lines files,
    effectively reducing memory consumption.
    Use ".gz" or ".gzip" extensions to dump the gzipped file.

    :param Iterable[str, Iterable[Any]] path_iterables: Iterable of iterables by filepath
    :param bool dump_if_empty: If false, don't create an empty JSON lines file.
    :param kwargs: `json.dumps` kwargs

    Examples:
        import jsonl

        path_iterables = (
            ("num.jsonl", ({"value": 1}, {"value": 2})),
            ("num.jsonl", ({"value": 3},)),
            ("foo.jsonl", ({"a": "1"}, {"b": 2})),
            ("baz.jsonl", ()),
        )
        jsonl.dump_fork(path_iterables)
    """

    def get_writer(dst):
        nothing = True
        with open_file(dst, mode="wt", encoding=utf_8) as fd:
            try:
                while True:
                    obj = yield
                    if nothing:
                        nothing = False
                    else:
                        fd.write(new_line)
                    fd.write(encoder(obj))
            except GeneratorExit:
                pass
        if nothing and not dump_if_empty:
            os.unlink(dst)

    encoder = functools.partial(dumps_line, **kwargs)
    writers = dict()

    for path, iterable in path_iterables:
        if path in writers:
            writer = writers[path]
        else:
            writer = get_writer(path)
            writer.send(None)
            writers[path] = writer

        for item in iterable:
            writer.send(item)
    # Cleanup
    for writer in writers.values():
        writer.close()


def load(fp, **kwargs):
    """
    Deserialize a file-like object containing JSON Lines into a Python iterable of objects.

    :param fp: file-like object
    :param kwargs: `json.loads` kwargs
    :rtype: Iterable[Any]

    Examples:
        import io
        import jsonl

        iterable = jsonl.load(io.StringIO('{"foo": 1}\n{"ño": 2}\n'))
        print(tuple(iterable))  # >> ({'foo': 1}, {'ño': 2})
    """

    decode = functools.partial(json.loads, **kwargs)
    yield from map(decode, fp)


def load_from(filename, **kwargs):
    """
    Deserialize a JSON Lines file into an iterable of Python objects.
    Recognizes ".gz" and ".gzip" extensions to load compressed files.

    :param filename: file path
    :param kwargs: `json.loads` kwargs
    :rtype: Iterable[Any]

    Examples:
        import jsonl

        iterable1 = jsonl.load_from("myfile.jsonl")
        iterable2 = jsonl.load_from("myfile.jsonl.gz")

        print(tuple(iterable1))
        print(tuple(iterable2))
    """

    with open_file(filename, mode="rt", encoding=utf_8) as f:
        yield from load(f, **kwargs)
