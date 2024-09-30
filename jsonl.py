# -*- coding: utf-8 -*-

"""
Useful functions for working with jsonlines data as described: https://jsonlines.org/

- 🌎 Offers an API similar to Python's built-in `json` module.
- 🚀 Supports serialization/deserialization using the most common `json` libraries, prioritizing `orjson`, then `ujson`,
  and defaulting to the standard `json` if the others are unavailable.
- 🗜️ Enables compression using `gzip`, `bzip2`, and `xz` formats.
- 🔧 Load files containing broken lines, skipping any malformed lines.
- 📦 Provides a simple API for incremental writing to multiple files.
"""

__version__ = "1.3.4"
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
import logging
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


def get_encoding(mode):
    return utf_8 if "t" in mode else None  # Text mode encoding is required.


def xopen(name, /, *, mode="rb", encoding=None):
    """
    Open file depending on a supported file extension.
    If the file extension is not recognized, the default `open` function is used.
    """

    default = open
    openers = {
        ".jsonl": default,
        ".gz": gzip.open,
        ".bz2": bz2.open,
        ".xz": lzma.open,
    }
    extension = os.path.splitext(name)[1]
    opener = openers.get(extension, default)
    return opener(name, mode=mode, encoding=encoding or get_encoding(mode))


def dumper(iterable, /, **json_dumps_kwargs):
    """Generator yielding JSON Lines."""

    serialize = functools.partial(dumps_line, **json_dumps_kwargs)
    for obj in iter(iterable):
        yield serialize(obj) + new_line


def loader(stream, broken, /, **json_loads_kwargs):
    """Generator yielding decoded JSON objects."""

    deserialize = functools.partial(json_loads, **json_loads_kwargs)
    for line in stream:
        try:
            string_line = line.decode(utf_8) if isinstance(line, bytes) else line
            yield deserialize(string_line)
        except Exception as e:
            logging.warning("Error deserializing line: %s", e)
            if not broken:
                raise


def dumps(iterable, /, **json_dumps_kwargs):
    """
    Serialize an iterable into a JSON Lines formatted string.

    :param Iterable[Any] iterable: Iterable of objects
    :param json_dumps_kwargs: Additional keywords to pass to `dumps` of `json` provider
    :rtype: str
    """

    return "".join(dumper(iterable, **json_dumps_kwargs))


def dump(iterable, file, /, *, opener=None, text_mode=True, **json_dumps_kwargs):
    """
    Dump an iterable to a JSON Lines file.

    :param Iterable[Any] iterable: Iterable of objects.
    :param Union[str, bytes, os.PathLike] file: File to dump.
        * If a file object is provided, the `writelines` or `write` methods will be used to write the string data.
    :param Callable opener: Custom function to open the file if a filename is provided.
    :param bool text_mode: If false, write bytes to the file.
    :param json_dumps_kwargs: Additional keywords to pass to `dumps` of `json` provider
    :raises ValueError: If the file object is missing the `writelines` and `write` methods.
    """

    lines = dumper(iterable, **json_dumps_kwargs)
    lines = lines if text_mode else (line.encode(utf_8) for line in lines)
    if isinstance(file, os.PathLike):
        file = os.fspath(file)
    if isinstance(file, str):  # No, it's a filename
        fd_mode = "wt" if text_mode else "wb"
        fd_open = opener or xopen
        with fd_open(file, mode=fd_mode, encoding=get_encoding(fd_mode)) as fd:
            fd.writelines(lines)
    elif hasattr(file, "writelines"):
        file.writelines(lines)
    elif hasattr(file, "write"):
        for line in lines:
            file.write(line)
    else:
        raise ValueError(
            "Invalid file object, missing `writelines` and `write` methods."
        )


def dump_fork(path_iterables, /, *, opener=None, text_mode=True, dump_if_empty=True, **json_dumps_kwargs):
    """
    Incrementally dumps multiple iterables into the specified jsonlines files,
    effectively reducing memory consumption.

    :param Iterable[str, Iterable[Any]] path_iterables: Iterable of iterables by filepath.
    :param Callable opener: Custom function to open the given file paths.
    :param bool text_mode: If false, write bytes to the file.
    :param bool dump_if_empty: If false, don't create an empty jsonlines file.
    :param json_dumps_kwargs: Additional keywords to pass to `dumps` of `json` provider
    """

    def get_writer(dst):
        nothing = True
        fd_mode = "wt" if text_mode else "wb"
        fd_open = opener or xopen
        with fd_open(dst, mode=fd_mode, encoding=get_encoding(fd_mode)) as fd:
            try:
                while True:
                    obj = yield
                    nothing = False
                    line = encoder(obj) + new_line
                    line = line if text_mode else line.encode(utf_8)
                    fd.write(line)
            except GeneratorExit:
                pass
        if nothing and not dump_if_empty:
            os.unlink(dst)

    encoder = functools.partial(dumps_line, **json_dumps_kwargs)
    writers = dict()
    try:
        for path, iterable in path_iterables:
            if path in writers:
                writer = writers[path]
            else:
                writer = get_writer(path)
                writer.send(None)
                writers[path] = writer

            for item in iterable:
                writer.send(item)
    finally:  # Cleanup
        for writer in writers.values():
            writer.close()


def load(file, /, *, opener=None, broken=False, **json_loads_kwargs):
    """
    Deserialize a UTF-8 encoded JSON Lines file into an iterable of Python objects.

    If the file's extension indicates a recognized compression format (.gz, .bz2, .xz),
    the corresponding decompression method is applied; if not, the standard open function is used by default.

    :param Union[str | bytes | os.PathLike] file: File to load
    :param Callable opener: Custom function to open the file if a filename is provided.
    :param bool broken: If true, skip broken lines (only logging a warning).
    :param json_loads_kwargs: Additional keywords to pass to `loads` of `json` provider.
    :rtype: Iterable[Any]
    """

    if isinstance(file, os.PathLike):
        file = os.fspath(file)
    if isinstance(file, str):  # No, it's a filename
        fd_open = opener or xopen
        with fd_open(file, mode="rb", encoding=None) as fd:
            yield from loader(fd, broken, **json_loads_kwargs)
    else:
        yield from loader(file, broken, **json_loads_kwargs)
