# -*- coding: utf-8 -*-

"""
Useful functions for working with jsonlines data as described: https://jsonlines.org/

Features:
- Exposes an API similar to the `json` module from the standard library.
- Supports `orjson`, `ujson` libraries or standard `json`.
- Supports `gzip` and `bzip2` compression formats.
"""

__version__ = "1.1.2"
__all__ = [
    "dump",
    "dumps",
    "dump_fork",
    "load",
]
__title__ = "py-jsonl"

import bz2
import functools
import gzip
import io
import json
import os

# Use the fastest available JSON library for serialization/deserialization, prioritizing `orjson`,
# then `ujson`, and defaulting to the standard `json` if none are installed.
try:
    import orjson
except ImportError:
    orjson = None

try:
    import ujson
except ImportError:
    ujson = None

json_dumps = (orjson or ujson or json).dumps
json_loads = (orjson or ujson or json).loads

empty = object()
dumps_line = functools.partial(
    json_dumps, ensure_ascii=False
)  # result can include non-ASCII characters
utf_8 = "utf-8"
new_line = "\n"
extensions = (".jsonl.gzip", ".jsonl.gz", ".jsonl.bz2", ".jsonl")


def is_binary_file(fp):
    mode = getattr(fp, "mode", None)
    return (isinstance(mode, str) and "b" in mode) or isinstance(
        fp, (io.BytesIO, gzip.GzipFile, bz2.BZ2File)
    )


def open_file(name, mode="rt", encoding=None):
    """Open file depending on supported file extension."""

    if not name.endswith(extensions):
        raise ValueError(name)
    elif name.endswith((".gz", ".gzip")):
        opener = gzip.open
    elif name.endswith(".bz2"):
        opener = bz2.open
    else:
        opener = open
    if "t" in mode:  # Text mode encoding is required.
        encoding = utf_8
    return opener(name, mode=mode, encoding=encoding)


def dumper(iterable, **kwargs):
    """Generator yielding jsonlines."""

    serialize = functools.partial(dumps_line, **kwargs)
    for obj in iter(iterable):
        yield serialize(obj)
        yield new_line


def loader(iterable, **kwargs):
    """Generator yielding decoded JSON objects."""

    deserialize = functools.partial(json_loads, **kwargs)
    lines = (
        line.decode(utf_8) if isinstance(line, bytes) else line
        for line in iter(iterable)
    )
    yield from map(deserialize, lines)


def dumps(iterable, **kwargs):
    """
    Serialize an iterable into a jsonlines formatted string.

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


def dump(iterable, file, **kwargs):
    """
    Dump an iterable to a jsonlines file.
    - Use (`.gz`, `.gzip`, `.bz2`) extensions to create a compressed dump of the file.
    - Dumps falls back to the following functions: (`orjson.dumps`, `ujson.dumps`, and `json.dumps`).

    :param Iterable[Any] iterable: Iterable of objects
    :param Union[str | bytes | os.PathLike | io.IOBase] file: File to dump
    :param kwargs: `json.dumps` kwargs

    Example:
        import jsonl

        data = ({'foo': 1}, {'bar': 2})
        jsonl.dump(data, "file1.jsonl")
    """

    lines = dumper(iterable, **kwargs)
    if isinstance(file, io.IOBase):  # file-like object
        # If it's a binary file, convert string to bytes
        lines = (
            (line.encode(utf_8) for line in lines) if is_binary_file(file) else lines
        )
        file.writelines(lines)
    else:
        with open_file(file, mode="wt", encoding=utf_8) as fp:
            fp.writelines(lines)


def dump_fork(path_iterables, dump_if_empty=True, **kwargs):
    """
    Incrementally dumps multiple iterables into the specified jsonlines files,
    effectively reducing memory consumption.

    - Use (`.gz`, `.gzip`, `.bz2`) extensions to dump the compressed file.
    - Dumps falls back to the following functions: (`orjson.dumps`, `ujson.dumps`, and `json.dumps`).

    :param Iterable[str, Iterable[Any]] path_iterables: Iterable of iterables by filepath
    :param bool dump_if_empty: If false, don't create an empty jsonlines file.
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


def load(file, **kwargs):
    """
    Deserialize a UTF-8-encoded jsonlines file into an iterable of Python objects.

    - Recognizes (`.gz`, `.gzip`, `.bz2`)  extensions to load compressed files.
    - Loads falls back to the following functions: (`orjson.loads`, `ujson.loads`, and `json.loads`).

    :param Union[str | bytes | os.PathLike | io.IOBase ] file: File to load
    :param kwargs: `json.loads` kwargs
    :rtype: Iterable[Any]

    Examples:
        import jsonl

        iterable = jsonl.load("file1.jsonl.gz")
        print(tuple(iterable))
    """

    if isinstance(file, io.IOBase):  # file-like object
        yield from loader(file, **kwargs)
    else:
        with open_file(file, mode="rt", encoding=utf_8) as fp:
            yield from loader(fp, **kwargs)
