# -*- coding: utf-8 -*-

"""
Useful functions for working with jsonlines data as described: https://jsonlines.org/

- Offers an API similar to Python's built-in `json` module.
- Supports serialization/deserialization using the most common `json` libraries, prioritizing `orjson`, then `ujson`,
  and defaulting to the standard `json` if the others are unavailable.
- Enables compression using `gzip`, `bzip2`, and `xz` formats.
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
import lzma
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
dumps_line = functools.partial(json_dumps, ensure_ascii=False)  # result can include non-ASCII characters
utf_8 = "utf-8"
new_line = "\n"
extensions = (".jsonl", ".gz", ".bz2", ".xz")


def is_binary_file(fp):
    mode = getattr(fp, "mode", None)
    compressed = (io.BytesIO, gzip.GzipFile, bz2.BZ2File, lzma.LZMAFile)
    return (isinstance(mode, str) and "b" in mode) or isinstance(fp, compressed)


def xopen(name, mode="rt", encoding=None):
    """Open file depending on supported file extension."""

    openers = {
        ".jsonl": open,
        ".gz": gzip.open,
        ".bz2": bz2.open,
        ".xz": lzma.open,
    }

    ext = os.path.splitext(name)[1]
    if fn := openers.get(ext):
        encoding = utf_8 if "t" in mode else None  # Text mode encoding is required.
        return fn(name, mode=mode, encoding=encoding)
    else:
        raise ValueError(name)


def dumper(iterable, **kwargs):
    """Generator yielding jsonlines."""

    serialize = functools.partial(dumps_line, **kwargs)
    for obj in iter(iterable):
        yield serialize(obj)
        yield new_line


def loader(iterable, **kwargs):
    """Generator yielding decoded JSON objects."""

    deserialize = functools.partial(json_loads, **kwargs)
    lines = (line.decode(utf_8) if isinstance(line, bytes) else line for line in iter(iterable))
    yield from map(deserialize, lines)


def dumps(iterable, **kwargs):
    """
    Serialize an iterable into a JSON Lines formatted string.

    :param Iterable[Any] iterable: Iterable of objects
    :param kwargs: `json.dumps` kwargs
    :rtype: str
    """

    return "".join(dumper(iterable, **kwargs))


def dump(iterable, file, **kwargs):
    """
    Dump an iterable to a JSON Lines file.

    :param Iterable[Any] iterable: Iterable of object
    :param Union[str | bytes | os.PathLike | io.IOBase] file: File to dump
    :param kwargs: `json.dumps` kwargs
    """

    lines = dumper(iterable, **kwargs)
    if isinstance(file, io.IOBase):  # file-like object
        # If it's a binary file, convert string to bytes
        lines = ((line.encode(utf_8) for line in lines) if is_binary_file(file) else lines)
        file.writelines(lines)
    else:
        with xopen(file, mode="wt", encoding=utf_8) as fp:
            fp.writelines(lines)


def dump_fork(path_iterables, dump_if_empty=True, **kwargs):
    """
    Incrementally dumps multiple iterables into the specified jsonlines files,
    effectively reducing memory consumption.

    :param Iterable[str, Iterable[Any]] path_iterables: Iterable of iterables by filepath
    :param bool dump_if_empty: If false, don't create an empty jsonlines file.
    :param kwargs: `json.dumps` kwargs
    """

    def get_writer(dst):
        nothing = True
        with xopen(dst, mode="wt", encoding=utf_8) as fd:
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
    Deserialize a UTF-8 encoded jsonlines file into an iterable of Python objects.

    :param Union[str | bytes | os.PathLike | io.IOBase ] file: File to load
    :param kwargs: `json.loads` kwargs
    :rtype: Iterable[Any]
    """

    if isinstance(file, io.IOBase):  # file-like object
        yield from loader(file, **kwargs)
    else:
        with xopen(file, mode="rt", encoding=utf_8) as fp:
            yield from loader(fp, **kwargs)
