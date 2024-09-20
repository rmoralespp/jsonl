# -*- coding: utf-8 -*-

"""
Useful functions for working with jsonlines data as described: https://jsonlines.org/

- Offers an API similar to Python's built-in `json` module.
- Supports serialization/deserialization using the most common `json` libraries, prioritizing `orjson`, then `ujson`,
  and defaulting to the standard `json` if the others are unavailable.
- Enables compression using `gzip`, `bzip2`, and `xz` formats.
"""

__version__ = "1.3.1"
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
import lzma
import os

# Use the fastest available JSON library for serialization/deserialization, prioritizing `orjson`,
# then `ujson`, and defaulting to the standard `json` if none are installed.
try:
    import orjson as json_module
except ImportError:
    try:
        import ujson as json_module
    except ImportError:
        import json as json_module

json_dumps = json_module.dumps
json_loads = json_module.loads

empty = object()
dumps_line = functools.partial(json_dumps, ensure_ascii=False)  # result can include non-ASCII characters
utf_8 = "utf-8"
new_line = "\n"
extensions = (".jsonl", ".gz", ".bz2", ".xz")


def xopen(name, mode="rt"):
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


def dumper(iterable, **json_dumps_kwargs):
    """Generator yielding JSON Lines."""

    serialize = functools.partial(dumps_line, **json_dumps_kwargs)
    for obj in iter(iterable):
        yield serialize(obj) + new_line


def loader(stream, **json_loads_kwargs):
    """Generator yielding decoded JSON objects."""

    deserialize = functools.partial(json_loads, **json_loads_kwargs)
    lines = (line.decode(utf_8) if isinstance(line, bytes) else line for line in iter(stream))
    yield from map(deserialize, lines)


def dumps(iterable, **json_dumps_kwargs):
    """
    Serialize an iterable into a JSON Lines formatted string.

    :param Iterable[Any] iterable: Iterable of objects
    :param json_dumps_kwargs: Additional keywords to pass to `dumps` of `json` provider
    :rtype: str
    """

    return "".join(dumper(iterable, **json_dumps_kwargs))


def dump(iterable, file, text_mode=True, **json_dumps_kwargs):
    """
    Dump an iterable to a JSON Lines file.

    :param Iterable[Any] iterable: Iterable of object
    :param Union[str, bytes, os.PathLike] file: File to dump.
        If a string, it's a filename; otherwise, a file object is expected to
        use `writelines` to write the string data.
    :param bool text_mode: If false, write bytes to the file.
    :param json_dumps_kwargs: Additional keywords to pass to `dumps` of `json` provider
    :raises ValueError: If the file object is missing the `writelines` method.
    """

    lines = dumper(iterable, **json_dumps_kwargs)
    if isinstance(file, os.PathLike):
        file = os.fspath(file)
    if isinstance(file, str):  # No, it's a filename
        with xopen(file, mode="wt") as fp:
            fp.writelines(lines)
    elif hasattr(file, "writelines"):
        lines = lines if text_mode else (line.encode(utf_8) for line in lines)
        file.writelines(lines)
    else:
        raise ValueError("Invalid file object, missing `writelines` method.")


def dump_fork(path_iterables, dump_if_empty=True, **json_dumps_kwargs):
    """
    Incrementally dumps multiple iterables into the specified jsonlines files,
    effectively reducing memory consumption.

    :param Iterable[str, Iterable[Any]] path_iterables: Iterable of iterables by filepath
    :param bool dump_if_empty: If false, don't create an empty jsonlines file.
    :param json_dumps_kwargs: Additional keywords to pass to `dumps` of `json` provider
    """

    def get_writer(dst):
        nothing = True
        with xopen(dst, mode="wt") as fd:
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

    encoder = functools.partial(dumps_line, **json_dumps_kwargs)
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


def load(file, **json_loads_kwargs):
    """
    Deserialize a UTF-8 encoded jsonlines file into an iterable of Python objects.

    :param Union[str | bytes | os.PathLike] file: File to load
    :param json_loads_kwargs: Additional keywords to pass to `loads` of `json` provider.
    :rtype: Iterable[Any]
    """

    if isinstance(file, os.PathLike):
        file = os.fspath(file)
    if isinstance(file, str):  # No, it's a filename
        with xopen(file, mode="rt") as fp:
            yield from loader(fp, **json_loads_kwargs)
    else:
        yield from loader(file, **json_loads_kwargs)
