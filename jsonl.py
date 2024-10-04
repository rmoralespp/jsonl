# -*- coding: utf-8 -*-

"""
Useful functions for working with jsonlines data as described: https://jsonlines.org/

- 🌎 Offers an API similar to Python's standard `json` module.
- 🚀 Supports custom serialization/deserialization callbacks. By default, it uses the standard `json` module.
- 🗜️ Enables compression using `gzip`, `bzip2`, and `xz` formats.
- 🔧 Load files containing broken lines, skipping any malformed lines.
- 📦 Provides a simple API for incremental writing to multiple files.
"""

__version__ = "1.3.7"
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
import json
import logging
import lzma
import os

empty = object()
utf_8 = "utf-8"
new_line = "\n"
new_line_bytes = b"\n"

default_json_dumps = functools.partial(json.dumps, ensure_ascii=False)  # result can include non-ASCII characters
default_json_loads = json.loads


def get_encoding(mode, /):
    return utf_8 if "t" in mode else None  # Text mode encoding is required.


def get_line(value, text_mode):
    if text_mode:
        line = value.decode(utf_8) if isinstance(value, bytes) else value
        resp = line + new_line
    else:
        line = value.encode(utf_8) if isinstance(value, str) else value
        resp = line + new_line_bytes
    return resp


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


def dumper(iterable, /, *, text_mode=True, json_dumps=None, **json_dumps_kwargs):
    """Generator yielding JSON Lines."""

    serialize = functools.partial(json_dumps or default_json_dumps, **json_dumps_kwargs)
    for obj in iter(iterable):
        value = serialize(obj)  # can be bytes, like "orjson.dumps".
        yield get_line(value, text_mode)


def loader(stream, broken, /, *, json_loads=None, **json_loads_kwargs):
    """Generator yielding decoded JSON objects."""

    deserialize = functools.partial(json_loads or default_json_loads, **json_loads_kwargs)
    for lineno, line in enumerate(stream, start=1):
        try:
            string_line = line.decode(utf_8) if isinstance(line, bytes) else line
            yield deserialize(string_line)
        except Exception as e:
            logging.warning("Broken line at %s: %s", lineno, e)
            if not broken:
                raise


def dumps(iterable, /, *, json_dumps=None, **json_dumps_kwargs):
    """
    Serialize an iterable into a JSON Lines formatted string.

    :param Iterable[Any] iterable: Iterable of objects
    :param Callable json_dumps: Custom function to serialize objects. By default, `json.dumps` is used.
    :param json_dumps_kwargs: Additional keywords to pass to `dumps` of `json` provider
    :rtype: str
    """

    return "".join(dumper(iterable, text_mode=True, json_dumps=json_dumps, **json_dumps_kwargs))


def dump(iterable, file, /, *, opener=None, text_mode=True, json_dumps=None, **json_dumps_kwargs):
    """
    Dump an iterable to a JSON Lines file.

    :param Iterable[Any] iterable: Iterable of objects.
    :param Union[str, bytes, os.PathLike] file: File to dump.
        * If a file object is provided, the `writelines` or `write` methods will be used to write the string data.
    :param Callable opener: Custom function to open the file if a filename is provided.
    :param bool text_mode: If false, write bytes to the file.
    :param Callable json_dumps: Custom function to serialize objects. By default, `json.dumps` is used.
    :param json_dumps_kwargs: Additional keywords to pass to `dumps` of `json` provider
    :raises ValueError: If the file object is missing the `writelines` and `write` methods.
    """

    lines = dumper(iterable, text_mode=text_mode, json_dumps=json_dumps, **json_dumps_kwargs)
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
        raise ValueError("Invalid file object, missing `writelines` and `write` methods.")


def dump_fork(paths, /, *, opener=None, text_mode=True, dump_if_empty=True, json_dumps=None, **json_dumps_kwargs):
    """
    Incrementally dumps multiple iterables into the specified jsonlines files,
    effectively reducing memory consumption.

    :param Iterable[str, Iterable[Any]] paths: Iterable of iterables by filepath.
    :param Callable opener: Custom function to open the given file paths.
    :param bool text_mode: If false, write bytes to the file.
    :param bool dump_if_empty: If false, don't create an empty jsonlines file.
    :param Callable json_dumps: Custom function to serialize objects. By default, `json.dumps` is used.
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
                    fd.write(get_line(encoder(obj), text_mode))
            except GeneratorExit:
                pass
        if nothing and not dump_if_empty:
            os.unlink(dst)

    encoder = functools.partial(json_dumps or default_json_dumps, **json_dumps_kwargs)
    writers = dict()
    try:
        for path, iterable in paths:
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


def load(file, /, *, opener=None, broken=False, json_loads=None, **json_loads_kwargs):
    """
    Deserialize a UTF-8 encoded JSON Lines file into an iterable of Python objects.

    If the file's extension indicates a recognized compression format (.gz, .bz2, .xz),
    the corresponding decompression method is applied; if not, the standard open function is used by default.

    :param Union[str | bytes | os.PathLike] file: File to load
    :param Callable opener: Custom function to open the file if a filename is provided.
    :param bool broken: If true, skip broken lines (only logging a warning).
    :param Callable json_loads: Custom function to deserialize JSON strings. By default, `json.loads` is used.
    :param json_loads_kwargs: Additional keywords to pass to `loads` of `json` provider.
    :rtype: Iterable[Any]
    """

    if isinstance(file, os.PathLike):
        file = os.fspath(file)
    if isinstance(file, str):  # No, it's a filename
        fd_open = opener or xopen
        with fd_open(file, mode="rb", encoding=None) as fd:
            yield from loader(fd, broken, json_loads=json_loads, **json_loads_kwargs)
    else:
        yield from loader(file, broken, json_loads=json_loads, **json_loads_kwargs)
