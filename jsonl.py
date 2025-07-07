"""Useful functions for working with jsonlines data as described: https://jsonlines.org/."""

__all__ = [
    "dump",
    "dumper",
    "dumps",
    "dump_fork",
    "load",
    "loader",
    "load_archive",
    "dump_archive",
]

import bz2
import contextlib
import fnmatch
import functools
import gzip
import json
import logging
import lzma
import os
import shutil
import tarfile
import tempfile
import zipfile

_utf_8 = "utf-8"
_new_line = "\n"
_new_line_bytes = b"\n"

_default_json_dumps = functools.partial(json.dumps, ensure_ascii=False)  # result can include non-ASCII characters
_default_json_loads = json.loads

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())


def _get_encoding(mode, /):
    """Get the encoding based on the file mode."""

    return _utf_8 if "t" in mode else None  # Text mode encoding is required.


def _get_line(value, text_mode, /):
    """Get a line from the value, ensuring it ends with a newline character."""

    if text_mode:
        line = value.decode(_utf_8) if isinstance(value, bytes) else value
        resp = line + _new_line
    else:
        line = value.encode(_utf_8) if isinstance(value, str) else value
        resp = line + _new_line_bytes
    return resp


def _xopen(name, /, *, mode="rb", encoding=None):
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
    return opener(name, mode=mode, encoding=encoding or _get_encoding(mode))


@contextlib.contextmanager
def _xfile(name, obj, /):
    """
    Context manager to handle file-like objects with automatic decompression.
    Does not close the file if it is the original object passed.

    :param str name: Filename or path to the file.
    :param obj: File-like an object.
    """

    if name.endswith(".gz"):
        file = gzip.GzipFile(fileobj=obj)
    elif name.endswith(".bz2"):
        file = bz2.BZ2File(obj)
    elif name.endswith(".xz"):
        file = lzma.LZMAFile(obj)  # noqa: SIM115
    else:
        file = obj

    try:
        yield file
    finally:
        if file is not obj:
            file.close()


def _get_archive_format(path, /):
    """Return a valid archive format for `shutil.make_archive` based on the filename."""

    formats = {
        "zip": "zip",
        "tar": "tar",
        "tar.gz": "gztar",
        "tar.bz2": "bztar",
        "tar.xz": "xztar",
    }
    basename = os.path.basename(path)
    _, _, ext = basename.partition(".")
    if fmt := formats.get(ext):
        return fmt
    else:
        raise ValueError(f"Unsupported archive extension: {path}")


def _del_archive_extension(path, /):
    dirpath, basename = os.path.split(path)
    arcpath = os.path.join(dirpath, basename.split(".")[0])
    return os.path.normpath(arcpath)


def _iterfind_zip_members(filename, pattern, pwd, /):
    with zipfile.ZipFile(filename) as zf:
        for name in fnmatch.filter(zf.namelist(), pattern):
            file = zf.open(name, pwd=pwd)
            with file:
                yield file


def _iterfind_tar_members(filename, pattern, /):
    with tarfile.open(filename) as archive:
        for name in fnmatch.filter(archive.getnames(), pattern):
            if file := archive.extractfile(name):
                with file:
                    yield file


def dumper(iterable, /, *, text_mode=True, json_dumps=None, **json_dumps_kwargs):
    """Dump an iterable of objects into JSON Lines format."""

    serialize = functools.partial(json_dumps or _default_json_dumps, **json_dumps_kwargs)
    for obj in iter(iterable):
        value = serialize(obj)  # can be bytes, like "orjson.dumps".
        yield _get_line(value, text_mode)


def loader(stream, broken, /, *, json_loads=None, **json_loads_kwargs):
    """Load a JSON Lines formatted stream into an iterable of Python objects."""

    deserialize = functools.partial(json_loads or _default_json_loads, **json_loads_kwargs)
    for lineno, line in enumerate(stream, start=1):
        try:
            string_line = line.decode(_utf_8) if isinstance(line, bytes) else line
            yield deserialize(string_line)
        except Exception as e:
            _logger.warning("Broken line at %s: %s", lineno, e)
            if not broken:
                raise


def dumps(iterable, /, *, json_dumps=None, **json_dumps_kwargs):
    """
    Serialize an iterable into a JSON Lines formatted string.

    :param Iterable[Any] iterable: Iterable of objects
    :param Optional[Callable] json_dumps: Custom function to serialize objects. By default, `json.dumps` is used.
    :param Unpack[dict] json_dumps_kwargs: Additional keywords to pass to `dumps` of `json` provider
    :rtype: str
    """

    return "".join(dumper(iterable, text_mode=True, json_dumps=json_dumps, **json_dumps_kwargs))


def dump(iterable, file, /, *, opener=None, text_mode=True, json_dumps=None, **json_dumps_kwargs):
    """
    Dump an iterable to a JSON Lines file.

    :param Iterable[Any] iterable: Iterable of objects.
    :param str | bytes | os.PathLike | Any file: File to dump.
        * If a file object is provided, the `writelines` or `write` methods will be used to write the string data.
    :param Optional[Callable] opener: Custom function to open the file if a filename is provided.
    :param bool text_mode: If false, write bytes to the file.
    :param Optional[Callable] json_dumps: Custom function to serialize objects. By default, `json.dumps` is used.
    :param Unpack[dict] json_dumps_kwargs: Additional keywords to pass to `dumps` of `json` provider
    :raises ValueError: If the file object is missing the `writelines` and `write` methods.
    """

    lines = dumper(iterable, text_mode=text_mode, json_dumps=json_dumps, **json_dumps_kwargs)
    if isinstance(file, os.PathLike):
        file = os.fspath(file)
    if isinstance(file, str):  # No, it's a filename
        fd_mode = "wt" if text_mode else "wb"
        fd_open = opener or _xopen
        with fd_open(file, mode=fd_mode, encoding=_get_encoding(fd_mode)) as fd:
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
    :param Optional[Callable] opener: Custom function to open the given file paths.
    :param bool text_mode: If false, write bytes to the file.
    :param bool dump_if_empty: If false, don't create an empty jsonlines file.
    :param Optional[Callable] json_dumps: Custom function to serialize objects. By default, `json.dumps` is used.
    :param Unpack[dict] json_dumps_kwargs: Additional keywords to pass to `dumps` of `json` provider
    """

    def get_writer(dst):
        nothing = True
        fd_mode = "wt" if text_mode else "wb"
        fd_open = opener or _xopen
        with fd_open(dst, mode=fd_mode, encoding=_get_encoding(fd_mode)) as fd:
            try:
                while True:
                    obj = yield
                    nothing = False
                    fd.write(_get_line(encoder(obj), text_mode))
            except GeneratorExit:
                pass
        if nothing and not dump_if_empty:
            os.unlink(dst)

    encoder = functools.partial(json_dumps or _default_json_dumps, **json_dumps_kwargs)
    writers = {}
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

    :param str | bytes | os.PathLike | Any file: File to load.
    :param Optional[Callable] opener: Custom function to open the file if a filename is provided.
    :param bool broken: If true, skip broken lines (only logging a warning).
    :param Optional[Callable] json_loads: Custom function to deserialize JSON strings. By default, `json.loads` is used.
    :param Unpack[dict] json_loads_kwargs: Additional keywords to pass to `loads` of `json` provider.
    :rtype: Iterable[Any]
    """

    if isinstance(file, os.PathLike):
        file = os.fspath(file)
    if isinstance(file, str):  # No, it's a filename
        openhook = opener or _xopen
        with openhook(file, mode="rb", encoding=None) as fd:
            yield from loader(fd, broken, json_loads=json_loads, **json_loads_kwargs)
    else:
        yield from loader(file, broken, json_loads=json_loads, **json_loads_kwargs)


def load_archive(
    file,
    /,
    *,
    pattern="*.jsonl",
    pwd=None,
    opener=None,
    broken=False,
    json_loads=None,
    **json_loads_kwargs,
):
    """
    Load JSON Lines files from an archive (zip or tar) matching a specific pattern.
    Tar archives can be compressed with gzip, bzip2, or xz. (e.g., `.tar.gz`, `.tar.bz2`, `.tar.xz`).

    :param str | bytes | os.PathLike | Any file: Archive file to load.
    :param str pattern: Pattern to match filenames inside the archive,
        following Unix shell-style wildcard rules as defined by `fnmatch`.
        For more details, see: https://docs.python.org/3/library/fnmatch.html

    :param Optional[bytes] pwd: The password to decrypt the archive, if applicable.
    :param Optional[Callable] opener: Custom function to open the file if a filename is provided.
    :param bool broken: If true, skip broken lines (only logging a warning).
    :param Optional[Callable] json_loads: Custom function to deserialize JSON strings. By default, `json.loads` is used.
    :param Unpack[dict] json_loads_kwargs: Additional keywords to pass to `loads` of `json` provider.
    :rtype: Generator[tuple[str, Generator[Any]]]
    """

    if zipfile.is_zipfile(file):
        members = _iterfind_zip_members(file, pattern, pwd)
    elif tarfile.is_tarfile(file):
        members = _iterfind_tar_members(file, pattern)
    else:
        raise ValueError(f"Unsupported archive format: {file}")

    for member in members:
        filename = member.name
        with _xfile(filename, member) as fp:
            it = load(fp, opener=opener, broken=broken, json_loads=json_loads, **json_loads_kwargs)
            yield (filename, it)


def dump_archive(
    path,
    items_by_relpath,
    /,
    *,
    opener=None,
    text_mode=True,
    dump_if_empty=True,
    json_dumps=None,
    **json_dumps_kwargs,
):
    """
    Dump multiple JSON Lines items into an archive file (zip or tar) with the specified path.
    - If the archive already exists on the given path, it will be overwritten.
    - Supports TAR compression with gzip (`.tar.gz`), bzip2 (`.tar.bz2`), or xz (`.tar.xz`).

    :param str path: Destination path for the archive file.
    :param Iterable[tuple[str, Iterable[Any]]] items_by_relpath:
        Iterable of (relative_path, items), where `relative_path` is the target file path within
        the archive, and `items` is an iterable of JSON-serializable objects.

    :param Optional[Callable] opener: Custom function to open the given file paths.
    :param bool text_mode: If false, write bytes to the file.
    :param bool dump_if_empty: If false, don't create an empty jsonlines file nor an empty archive.
    :param Optional[Callable] json_dumps: Custom function to serialize objects. By default, `json.dumps` is used.
    :param Unpack[dict] json_dumps_kwargs: Additional keywords to pass to `dumps` of `json` provider

    :raises ValueError: If a filepath in `items_by_relpath` is absolute, or if the archive extension is unsupported.
    :return: Path to the created archive file, or `None` if no items were dumped and `dump_if_empty` is `False`.
    """

    def items_by_abspath(root_dir, /):
        for file_relpath, data in items_by_relpath:
            if os.path.isabs(file_relpath):
                raise ValueError(f"Absolute path is not allowed: {file_relpath}")

            file_abspath = os.path.join(root_dir, file_relpath)
            file_dirpath = os.path.dirname(file_abspath)
            if not os.path.exists(file_dirpath):
                os.makedirs(file_dirpath)  # Ensure the directory exists
            yield (file_abspath, data)

    # Validate the archive format before proceeding to dump.
    arc_fmt = _get_archive_format(path)
    archive = _del_archive_extension(path)
    # Dump the items to a temporary directory.
    with tempfile.TemporaryDirectory() as tmpdir:
        dump_fork(
            items_by_abspath(tmpdir),
            opener=opener,
            text_mode=text_mode,
            dump_if_empty=dump_if_empty,
            json_dumps=json_dumps,
            **json_dumps_kwargs,
        )
        if dump_if_empty or os.listdir(tmpdir):
            # Create the archive from the temporary directory.
            return shutil.make_archive(archive, arc_fmt, root_dir=tmpdir, logger=_logger)
        else:
            return None
