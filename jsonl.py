# -*- coding: utf-8 -*-

"""Useful functions for working with jsonlines data as described: https://jsonlines.org/."""

__all__ = [
    "dump",
    "dumper",
    "dumps",
    "dump_fork",
    "load",
    "loader",
    "loads",
    "load_archive",
    "dump_archive",
    "main",
]

import argparse
import bz2
import collections
import contextlib
import errno
import fnmatch
import functools
import gzip
import io
import json
import logging
import lzma
import os
import shutil
import string
import sys
import tarfile
import tempfile
import urllib.parse
import urllib.request
import zipfile

try:
    from compression import zstd
except ImportError:
    zstd = None  # Python < 3.14

# ---------------------------------- Internal variables ----------------------------------

_utf_8 = "utf-8"
_new_line = "\n"
_new_line_bytes = b"\n"

_default_decode = json.JSONDecoder().decode
_default_encode = json.JSONEncoder(
    ensure_ascii=False,  # result can include non-ASCII characters
).encode

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

_path_types = (str, bytes, os.PathLike)
_default_max_open_files = 64

ext_jsonl = ".jsonl"
ext_ndjson = ".ndjson"
ext_gz = ".gz"
ext_bz2 = ".bz2"
ext_xz = ".xz"
ext_zst = ".zst"

_compression_signatures = (
    (ext_gz, b"\x1f\x8b"),
    (ext_bz2, b"\x42\x5a\x68"),
    (ext_xz, b"\xfd\x37\x7a\x58\x5a\x00"),
    (ext_zst, b"\x28\xb5\x2f\xfd"),
)
extensions = {ext_jsonl, ext_gz, ext_bz2, ext_xz}
_known_extensions = extensions | {ext_zst}
_openers = {
    ext_jsonl: open,
    ext_gz: gzip.open,
    ext_bz2: bz2.open,
    ext_xz: lzma.open,
}
_archive_formats = {
    "zip": "zip",
    "tar": "tar",
    "tar.gz": "gztar",
    "tar.bz2": "bztar",
    "tar.xz": "xztar",
}
_archive_member_formats = (ext_jsonl, ext_ndjson)
_archive_member_compression_suffixes = ("", ext_gz, ext_bz2, ext_xz)

if zstd is None:
    _logger.info("zstd compression is not available!")
else:
    extensions.add(ext_zst)
    _openers[ext_zst] = zstd.open
    _archive_formats["tar.zst"] = "zstdtar"
    _archive_member_compression_suffixes += (ext_zst,)

_default_archive_member_suffixes = tuple(
    format_ + compression
    for format_ in _archive_member_formats
    for compression in _archive_member_compression_suffixes
)

# ---------------------------------- Internal utils ----------------------------------


def _extension_from_magic(head, /):
    """Detect a compression extension from the leading magic bytes, or None."""

    for extension, signature in _compression_signatures:
        if head.startswith(signature):
            return extension
    return None


def _get_path(value, /):
    """Return a string path, rejecting ambiguous bytes paths."""

    path = os.fspath(value)
    if isinstance(path, bytes):
        raise TypeError("bytes paths are not supported; decode the path with os.fsdecode()")
    return path


def _get_fileobj_extension(fileobj, /):
    """Get the file extension based on the initial bytes of a file-like object."""

    fd_position = fileobj.tell()  # Save current position
    fileobj.seek(0)  # Go to the start of the file
    bytes_ = fileobj.read(6)  # Read enough bytes to detect compression
    fileobj.seek(fd_position)  # Restore the original position
    return _extension_from_magic(bytes_)


def _decompressor(extension, fileobj, /):
    """Wrap a binary file object with the decompressor matching the extension (or return it as-is)."""

    if extension == ext_gz:
        return gzip.GzipFile(fileobj=fileobj)
    elif extension == ext_bz2:
        return bz2.BZ2File(fileobj)
    elif extension == ext_xz:
        return lzma.LZMAFile(fileobj)
    elif extension == ext_zst:
        if zstd is None:
            raise RuntimeError("Zstandard compression is unavailable in this Python runtime")
        return zstd.ZstdFile(fileobj)
    else:
        return fileobj


def _get_file_extension(name, mode, /, *, fileobj=None):
    """Get the file extension based on the filename or file-like object."""

    name = _get_path(name)
    extension = os.path.splitext(name)[1]
    if extension in _known_extensions:
        return extension
    elif mode == "rb" and fileobj:
        return _get_fileobj_extension(fileobj)
    elif "r" in mode:  # if not fileobj, try to open the file and detect from content
        with open(name, "rb") as fd:
            return _get_fileobj_extension(fd)
    else:
        return None


def _looks_like_url(value, /):
    if isinstance(value, urllib.request.Request):
        value = value.full_url
    if not isinstance(value, str):
        return False
    scheme = urllib.parse.urlparse(value)[0]
    if not scheme:
        return False
    # On Windows, a single-letter scheme like "C" in "C:/path" is a drive letter, not a URL
    if sys.platform == 'win32' and len(scheme) == 1 and scheme in string.ascii_letters:
        return False
    return True


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

    extension = _get_file_extension(name, mode)
    if extension == ext_zst and zstd is None:
        raise RuntimeError("Zstandard compression is unavailable in this Python runtime")
    opener = _openers.get(extension, open)
    return opener(name, mode=mode, encoding=encoding or _get_encoding(mode))


class _PrefixedReader(io.RawIOBase):
    """Read a captured prefix before continuing with the original binary stream."""

    def __init__(self, prefix, stream):
        super().__init__()
        self._prefix = io.BytesIO(prefix)
        self._stream = stream

    def readable(self):
        return True

    def readinto(self, buffer):
        view = memoryview(buffer)
        size = self._prefix.readinto(view)
        if size:
            return size

        read = getattr(self._stream, "read1", self._stream.read)
        chunk = read(len(view))
        if not chunk:
            return 0
        view[: len(chunk)] = chunk
        return len(chunk)


def _read_compression_prefix(stream, /):
    """Read only enough bytes to identify compression, stopping early for plain data."""

    head = bytearray()
    max_size = max(len(signature) for _extension, signature in _compression_signatures)
    while len(head) < max_size:  # pragma: no branch - every full-length signature exits in the loop
        byte = stream.read(1)
        if not byte:
            break
        head.extend(byte)
        if _extension_from_magic(head) is not None:
            break
        if not any(signature.startswith(head) for _extension, signature in _compression_signatures):
            break
    return bytes(head)


@contextlib.contextmanager
def _decompress_stream(stream, /, *, extension=None):
    """Yield a binary stream with transparent decompression without closing the source."""

    buffered = None
    file = stream
    try:
        if extension is None:
            head = _read_compression_prefix(stream)
            buffered = io.BufferedReader(_PrefixedReader(head, stream))
            extension = _extension_from_magic(head)
            file = buffered
        file = _decompressor(extension, file)
        yield file
    finally:
        try:
            if file is not stream:
                file.close()
        finally:
            if buffered is not None and not buffered.closed:
                buffered.close()


def _is_binary_stream(stream, /):
    """Return whether a file-like object exposes binary reads."""

    if isinstance(stream, io.TextIOBase):
        return False
    if isinstance(stream, (io.RawIOBase, io.BufferedIOBase)):
        return True
    read = getattr(stream, "read", None)
    return read is not None and isinstance(read(0), (bytes, bytearray))


@contextlib.contextmanager
def _xfile(name, obj, /):
    """
    Context manager to handle file-like objects with automatic decompression.

    Does not close the file if it is the original object passed.

    :param str name: Filename or path to the file.
    :param obj: File-like an object.
    """

    extension = os.path.splitext(_get_path(name))[1]
    if extension not in _known_extensions:
        extension = None
    with _decompress_stream(obj, extension=extension) as file:
        yield file


def _get_archive_extension(path, /):
    """Return the supported archive extension at the end of a path."""

    basename = os.path.basename(_get_path(path))
    for extension in sorted(_archive_formats, key=len, reverse=True):
        if basename.endswith("." + extension):
            return extension
    raise ValueError(f"Unsupported archive extension: {path}")


def _get_archive_format(path, /):
    """Return a valid archive format for `shutil.make_archive` based on the filename."""

    return _archive_formats[_get_archive_extension(path)]


def _del_archive_extension(path, /):
    path = _get_path(path)
    extension = _get_archive_extension(path)
    return os.path.normpath(path[: -(len(extension) + 1)])


def _get_archive_member_path(root_dir, relpath, /):
    """Resolve an archive member path, ensuring it remains below the staging directory."""

    file_relpath = _get_path(relpath)
    if os.path.isabs(file_relpath):
        raise ValueError(f"Absolute path is not allowed: {file_relpath}")

    root_dir = os.path.realpath(root_dir)
    file_abspath = os.path.realpath(os.path.join(root_dir, file_relpath))
    try:
        contained = os.path.commonpath((root_dir, file_abspath)) == root_dir
    except ValueError:
        contained = False
    if not contained:
        raise ValueError(f"Archive member path escapes the staging directory: {file_relpath}")
    return file_abspath


def _filter_archive_members(names, pattern, /):
    """Filter archive member names using the default suffixes or an explicit pattern."""

    if pattern is None:
        return [name for name in names if name.endswith(_default_archive_member_suffixes)]
    return fnmatch.filter(names, pattern)


def _iterfind_zip_members(name_or_obj, pattern, pwd, /):
    with zipfile.ZipFile(name_or_obj) as zf:
        for name in _filter_archive_members(zf.namelist(), pattern):
            file = zf.open(name, pwd=pwd)
            with file:
                yield file


def _iterfind_tar_members(name_or_obj, pattern, /):
    args, kwargs = (), {}
    if isinstance(name_or_obj, io.BytesIO):
        name_or_obj.seek(0)  # Ensure the pointer is at the start
        kwargs = {"fileobj": name_or_obj, "mode": "r:*"}
    else:
        args = (name_or_obj,)
    with tarfile.open(*args, **kwargs) as archive:
        for name in _filter_archive_members(archive.getnames(), pattern):
            if file := archive.extractfile(name):
                with file:
                    yield file


def _issubclass(o, klass):
    try:
        return issubclass(o, klass)
    except TypeError:
        return False


def _get_encode(cls, kwargs):
    if not (cls or kwargs):
        encode = _default_encode
    elif not cls:
        encode = json.JSONEncoder(**kwargs).encode
    elif _issubclass(cls, json.JSONEncoder):
        encode = cls(**kwargs).encode
    else:
        encode = functools.partial(cls, **kwargs)
    return encode


def _get_decode(cls, kwargs):
    if not (cls or kwargs):
        decode = _default_decode
    elif not cls:
        decode = json.JSONDecoder(**kwargs).decode
    elif _issubclass(cls, json.JSONDecoder):
        decode = cls(**kwargs).decode
    else:
        decode = functools.partial(cls, **kwargs)
    return decode

# ---------------------------------- Public API ----------------------------------


def dumper(iterable, /, *, text_mode=True, cls=None, **kwargs):
    """Dump an iterable of objects into JSON Lines format."""

    encode = _get_encode(cls, kwargs)
    for obj in iterable:
        value = encode(obj)  # can be bytes, like "orjson.dumps".
        yield _get_line(value, text_mode)


def loader(stream, broken, /, *, cls=None, _on_error=None, **kwargs):
    """Load a JSON Lines formatted stream into an object iterator."""

    decode = _get_decode(cls, kwargs)
    is_bytes = None
    for lineno, line in enumerate(stream, start=1):
        if is_bytes is None:  # Avoid "isinstance" check on every line after the first one.
            is_bytes = isinstance(line, bytes)
        try:
            yield decode(line.decode(_utf_8) if is_bytes else line)
        except Exception as e:
            if _on_error is not None:
                _on_error(lineno, e)
            _logger.warning("Broken line at %s: %s", lineno, e)
            if not broken:
                raise


def _load_stream(stream, broken, /, *, extension=None, encoding=None, cls=None, _on_error=None, **kwargs):
    """Load records from a text or binary stream with transparent decompression."""

    if _is_binary_stream(stream):
        with _decompress_stream(stream, extension=extension) as binary_stream:
            if encoding is None:
                yield from loader(binary_stream, broken, cls=cls, _on_error=_on_error, **kwargs)
            else:
                with io.TextIOWrapper(binary_stream, encoding=encoding) as text_stream:
                    yield from loader(text_stream, broken, cls=cls, _on_error=_on_error, **kwargs)
    else:
        yield from loader(stream, broken, cls=cls, _on_error=_on_error, **kwargs)


def dumps(iterable, /, *, cls=None, **kwargs):
    """
    Serialize an iterable into a JSON Lines formatted string.

    :param Iterable[Any] iterable: Iterable of objects
    :param Optional[Callable] cls: Custom `json.JSONEncoder` subclass (defaults to `json.JSONEncoder`).
    :param Unpack[dict] kwargs: keyword arguments used to configure the `JSONEncoder`.
    :rtype: str
    """

    return "".join(dumper(iterable, text_mode=True, cls=cls, **kwargs))


def loads(text, /, *, broken=False, cls=None, **kwargs):
    """
    Deserialize a JSON Lines formatted string into an object iterator.

    :param str text: JSON Lines formatted string.
    :param bool broken: If true, skip broken lines (only logging a warning).

    :param Optional[type[json.JSONDecoder] | Callable[..., Any]] cls: Custom decoder (defaults to `json.JSONDecoder`)
        - JSONDecoder subclass
        - Callable accepting arbitrary arguments and returning a decoded object
    :param Unpack[dict] kwargs: keyword arguments used to pass the Custom decoder (`cls`).

    :rtype: Iterator[Any]
    """

    # io.StringIO iteration is C-implemented and yields lines lazily without
    # allocating an intermediate list, unlike str.splitlines().
    yield from loader(io.StringIO(text), broken, cls=cls, **kwargs)


def dump(iterable, file, /, *, opener=None, text_mode=True, cls=None, **kwargs):
    """
    Dump an iterable to a JSON Lines file.

    :param Iterable[Any] iterable: Iterable of objects.
    :param str | os.PathLike[str] | Any file: File to dump.
        * If a file object is provided, the `writelines` or `write` methods will be used to write the string data.
    :param Optional[Callable] opener: Custom function to open the file if a filename is provided.
    :param bool text_mode: If false, write bytes to the file.

    :param Optional[type[json.JSONEncoder] | Callable[..., Any]] cls: Custom encoder (defaults to `json.JSONEncoder`)
        - JSONEncoder subclass
        - Callable accepting arbitrary arguments and returning an encoded object
    :param Unpack[dict] kwargs: keyword arguments used to pass the Custom encoder (`cls`).

    :raises ValueError: If the file object is missing the `writelines` and `write` methods.
    """

    lines = dumper(iterable, text_mode=text_mode, cls=cls, **kwargs)
    if isinstance(file, _path_types):
        file = _get_path(file)
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


def dump_fork(
    paths,
    /,
    *,
    opener=None,
    text_mode=True,
    dump_if_empty=True,
    max_open_files=_default_max_open_files,
    cls=None,
    **kwargs,
):
    """
    Incrementally dumps multiple iterables into the specified jsonlines files, effectively reducing memory consumption.

    :param Iterable[str | os.PathLike[str], Iterable[Any]] paths: Iterable of iterables by filepath.
    :param Optional[Callable] opener: Custom function to open the given file paths.
    :param bool text_mode: If false, write bytes to the file.
    :param bool dump_if_empty: If false, don't create an empty jsonlines file.
    :param Optional[int] max_open_files: Maximum number of destination files kept open simultaneously.
        If `None`, keep every destination open until dumping finishes.

    :param Optional[type[json.JSONEncoder] | Callable[..., Any]] cls: Custom encoder (defaults to `json.JSONEncoder`)
        - JSONEncoder subclass
        - Callable accepting arbitrary arguments and returning an encoded object
    :param Unpack[dict] kwargs: keyword arguments used to pass the Custom encoder (`cls`).
    """

    if max_open_files is not None and (isinstance(max_open_files, bool) or not isinstance(max_open_files, int)):
        raise TypeError("max_open_files must be an integer")
    if max_open_files is not None and max_open_files < 1:
        raise ValueError("max_open_files must be greater than zero")

    def get_writer(dst, append):
        fd_mode = ("a" if append else "w") + ("t" if text_mode else "b")
        fd_open = opener or _xopen
        with fd_open(dst, mode=fd_mode, encoding=_get_encoding(fd_mode)) as fd:
            try:
                while True:
                    obj = yield
                    fd.write(_get_line(encode(obj), text_mode))
                    path_states[dst] = True
            except GeneratorExit:
                # Flush compressor buffers before closing the generator to
                # ensure a valid end-of-stream marker (required for .gz/.xz/.zst in Python 3.14+)
                fd.flush()

        if not path_states[dst] and not dump_if_empty:
            os.unlink(dst)

    def close_writers():
        first_error = None
        while writers:
            _path, writer = writers.popitem()
            try:
                writer.close()
            except BaseException as error:
                if first_error is None:
                    first_error = error
                else:
                    _logger.error(
                        "Failed to close an additional dump_fork writer",
                        exc_info=(type(error), error, error.__traceback__),
                    )
        if first_error is not None:
            raise first_error

    encode = _get_encode(cls, kwargs)
    writers = collections.OrderedDict()
    path_states = {}

    def write_paths():
        for xpath, iterable in paths:
            path = _get_path(xpath)
            if path in writers:
                writer = writers.pop(path)
            else:
                if max_open_files is not None and len(writers) == max_open_files:
                    _old_path, old_writer = writers.popitem(last=False)
                    try:
                        old_writer.close()
                    except BaseException:
                        _logger.exception("Failed to close an evicted dump_fork writer")
                        raise

                writer = get_writer(path, append=path in path_states)
                writer.send(None)
                path_states.setdefault(path, False)

            writers[path] = writer
            for item in iterable:
                writer.send(item)

    try:
        write_paths()
    except BaseException:
        try:
            close_writers()
        except BaseException:
            _logger.exception("Failed to close a dump_fork writer while handling another error")
        raise
    else:
        close_writers()


def load(source, /, *, opener=None, broken=False, cls=None, _on_error=None, **kwargs):
    """
    Deserialize a UTF-8 encoded JSON Lines source—such as a filename, URL, or file-like object—into an object iterator.

    Compression is detected from local path extensions or magic bytes. URL responses and binary file-like objects
    are inspected without seeking and without consuming bytes from the resulting stream.

    :param str | os.PathLike[str] | urllib.request.Request | Any source:
        If a URL or `urllib.request.Request` object is provided, the file will be retrieved
        remotely using `urllib.request.urlopen`.
        For more details, see: https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen
    :param Optional[Callable] opener: Custom function to open the file if a filename is provided.
    :param bool broken: If true, skip broken lines (only logging a warning).

    :param Optional[type[json.JSONDecoder] | Callable[..., Any]] cls: Custom decoder (defaults to `json.JSONDecoder`)
        - JSONDecoder subclass
        - Callable accepting arbitrary arguments and returning a decoded object
    :param _on_error: Callback for reporting errors
    :param Unpack[dict] kwargs: keyword arguments used to pass the Custom decoder (`cls`).

    :rtype: Iterator[Any]
    """

    # URL or Request object handling
    if _looks_like_url(source):
        if opener is not None:
            raise ValueError("Custom opener is not supported for URLs or Request objects.")
        with urllib.request.urlopen(source) as fd:
            charset = fd.headers.get_content_charset(failobj=_utf_8)
            yield from _load_stream(
                fd,
                broken,
                encoding=charset,
                cls=cls,
                _on_error=_on_error,
                **kwargs,
            )
    # Filename handling
    elif isinstance(source, _path_types):
        filename = _get_path(source)
        openhook = opener or open
        extension = None if opener is not None else os.path.splitext(filename)[1]
        if extension not in _known_extensions:
            extension = None
        with openhook(filename, mode="rb", encoding=None) as fd:
            yield from _load_stream(
                fd,
                broken,
                extension=extension,
                cls=cls,
                _on_error=_on_error,
                **kwargs,
            )
    # File-like object handling
    else:
        yield from _load_stream(source, broken, cls=cls, _on_error=_on_error, **kwargs)


def load_archive(
    file,
    /,
    *,
    pattern=None,
    pwd=None,
    opener=None,
    broken=False,
    chunk_size=64 * 1024,
    cls=None,
    _on_error=None,
    **kwargs,
):
    """
    Load JSON Lines files from an archive (zip or tar) matching a specific pattern.

    When `pattern` is `None`, only members with a recognized JSON Lines suffix are loaded:
    `.jsonl`, `.ndjson`, or one of those suffixes followed by a supported compression suffix.

    Tar archives can be compressed with gzip, bzip2, xz or zst (Python +3.14). (e.g., `.tar.gz`, `.tar.bz2`, `.tar.xz`).

    :param str | bytes | os.PathLike | urllib.request.Request | Any file: Archive file to load.
        If a URL or `urllib.request.Request` object is provided, the file will be retrieved
        remotely using `urllib.request.urlopen`.
        For more details, see: https://docs.python.org/3/library/urllib.request.html#urllib.request.urlopen

    :param Optional[str] pattern: Pattern to match filenames inside the archive,
        following Unix shell-style wildcard rules as defined by `fnmatch`. If `None`, load only
        members with recognized JSON Lines suffixes. Automatic suffix matching is case-sensitive.
        For more details, see: https://docs.python.org/3/library/fnmatch.html

    :param Optional[bytes] pwd: The password to decrypt the archive, if applicable.
    :param Optional[Callable] opener: Custom function to open the file if a filename is provided.
    :param bool broken: If true, skip broken lines (only logging a warning).
    :param int chunk_size:
        The size (in bytes) of chunks when reading from a URL to avoid loading the entire file into memory at once.
        Default is 64 KB (64 * 1024 bytes).

    :param Optional[type[json.JSONDecoder] | Callable[..., Any]] cls: Custom decoder (defaults to `json.JSONDecoder`)
        - JSONDecoder subclass
        - Callable accepting arbitrary arguments and returning a decoded object
    :param _on_error: Callback for reporting errors
    :param Unpack[dict] kwargs: keyword arguments used to pass the Custom decoder (`cls`).

    :rtype: Iterator[tuple[str, Iterator[Any]]]
    """

    is_url = _looks_like_url(file)
    if not is_url and isinstance(file, _path_types):
        file = _get_path(file)

    with tempfile.TemporaryDirectory() as tmp:

        if is_url:
            if opener is not None:
                raise ValueError("Custom opener is not supported for URLs or Request objects.")

            # If a URL or request obj is provided, first download the file incrementally
            # to avoid loading the entire file into memory.
            tmp_path = os.path.join(tmp, "archive")
            with urllib.request.urlopen(file) as src_fd, open(tmp_path, mode="wb") as tmp_fd:
                for block in iter(functools.partial(src_fd.read, chunk_size), b''):
                    tmp_fd.write(block)
            file = tmp_path

        if zipfile.is_zipfile(file):
            members = _iterfind_zip_members(file, pattern, pwd)
        elif tarfile.is_tarfile(file):
            members = _iterfind_tar_members(file, pattern)
        else:
            raise ValueError("Unsupported archive format")

        for member in members:
            filename = member.name
            with _xfile(filename, member) as fp:
                it = load(fp, opener=opener, broken=broken, cls=cls, _on_error=_on_error, **kwargs)
                yield (filename, it)


def dump_archive(
    path,
    data,
    /,
    *,
    opener=None,
    text_mode=True,
    dump_if_empty=True,
    max_open_files=_default_max_open_files,
    cls=None,
    **kwargs,
):
    """
    Dump multiple JSON Lines items into an archive file (zip or tar) with the specified path.

    - If the archive already exists on the given path, it will be overwritten.
    - Supports TAR compression with gzip (`.tar.gz`), bzip2 (`.tar.bz2`), xz (`.tar.xz`),
      or zst (`.tar.zst`) (Python +3.14)

    :param str | os.PathLike[str] path: Destination path for the archive file.
    :param Iterable[tuple[str | os.PathLike[str], Iterable[Any]]] data:
        Iterable of (relative_path, items), where `relative_path` is the target file path within
        the archive, and `items` is an iterable of JSON-serializable objects.

    :param Optional[Callable] opener: Custom function to open the given file paths.
    :param bool text_mode: If false, write bytes to the file.
    :param bool dump_if_empty: If false, don't create an empty jsonlines file nor an empty archive.
    :param Optional[int] max_open_files: Maximum number of archive member files kept open simultaneously.
        If `None`, keep every member file open until dumping finishes.

    :param Optional[type[json.JSONEncoder] | Callable[..., Any]] cls: Custom encoder (defaults to `json.JSONEncoder`)
        - JSONEncoder subclass
        - Callable accepting arbitrary arguments and returning an encoded object
    :param Unpack[dict] kwargs: keyword arguments used to pass the Custom encoder (`cls`).

    :raises ValueError:
        If a filepath in `items_by_relpath` is absolute or escapes the staging directory,
        or if the archive extension is unsupported.
    :return: Path to the created archive file, or `None` if no items were dumped and `dump_if_empty` is `False`.
    """

    path = _get_path(path)

    def worker(root_dir, /):
        for relpath, iterable in data:
            file_abspath = _get_archive_member_path(root_dir, relpath)
            file_dirpath = os.path.dirname(file_abspath)
            os.makedirs(file_dirpath, exist_ok=True)
            yield (file_abspath, iterable)

    # Validate the archive format before proceeding to dump.
    arc_fmt = _get_archive_format(path)
    archive = _del_archive_extension(path)
    # Dump the items to a temporary directory.
    with tempfile.TemporaryDirectory() as tmpdir:
        dump_fork(
            worker(tmpdir),
            opener=opener,
            text_mode=text_mode,
            dump_if_empty=dump_if_empty,
            max_open_files=max_open_files,
            cls=cls,
            **kwargs,
        )
        if dump_if_empty or os.listdir(tmpdir):
            # Create the archive from the temporary directory.
            return shutil.make_archive(archive, arc_fmt, root_dir=tmpdir, logger=_logger)
        else:
            return None


# ---------------------------------- Command-line interface ----------------------------------

# Exit codes:
#   0 -> success, all records valid
#   1 -> one or more invalid JSON records were encountered
#   2 -> invalid command-line usage or input/output configuration error (argparse default)
#   3 -> unexpected I/O, filesystem, archive, compression, or runtime error
_EXIT_OK = 0
_EXIT_INVALID_RECORD = 1
_EXIT_RUNTIME_ERROR = 3


def _get_version():
    """Return the installed package version, or "unknown" when not available."""

    try:
        import importlib.metadata

        return importlib.metadata.version("py-jsonl")
    except Exception:
        return "unknown"


class _BrokenRecordReporter:
    """Report and count broken records independently of logging configuration."""

    def __init__(self):
        self.count = 0

    def __call__(self, lineno, error):
        self.count += 1
        print("jsonl: Broken line at {}: {}".format(lineno, error), file=sys.stderr)


def _cli_records(infile, broken, member, on_error, /):
    """Yield decoded records from the CLI input, reusing the streaming public API."""

    if member is not None or _is_archive_path(infile):
        pattern = member
        found = False
        for _name, items in load_archive(infile, pattern=pattern, broken=broken, _on_error=on_error):
            found = True
            yield from items
        if not found:
            description = pattern if pattern is not None else "default JSON Lines suffixes"
            raise ValueError("no archive members matched pattern {!r}".format(description))
    elif infile is None or infile == "-":
        yield from load(sys.stdin.buffer, broken=broken, _on_error=on_error)
    else:
        yield from load(infile, broken=broken, _on_error=on_error)


@contextlib.contextmanager
def _atomic_output(dest, /):
    """
    Yield a temporary path that atomically replaces `dest` on success.

    The temporary file is removed if the body raises, and the existing
    destination is left untouched until the replacement succeeds.
    """

    dest = os.path.abspath(_get_path(dest))
    dest_dir = os.path.dirname(dest)

    # Same filesystem keeps os.replace() atomic; the prefix makes cleanup remnants identifiable.
    with tempfile.TemporaryDirectory(dir=dest_dir, prefix=".jsonl-tmp-") as tmp_dir:
        tmp = os.path.join(tmp_dir, os.path.basename(dest))
        yield tmp

        # Keep an existing destination's permissions. For a new destination,
        # dump() creates `tmp` normally, so the process umask is applied.
        with contextlib.suppress(FileNotFoundError):
            shutil.copymode(dest, tmp)

        os.replace(tmp, dest)  # atomically publish only after successful completion


def _cli_write(records, outfile, encoder_kwargs, /):
    """Write records to stdout (streaming) or atomically to an output file."""

    if outfile is None:
        # Emit UTF-8 regardless of the platform's console/locale encoding so the
        # default non-ASCII output cannot raise UnicodeEncodeError (e.g. a Windows
        # cp1252 console). File output is already written as UTF-8 by `dump`.
        with contextlib.suppress(AttributeError, ValueError, OSError):
            sys.stdout.reconfigure(encoding="utf-8")
        dump(records, sys.stdout, **encoder_kwargs)
    else:
        with _atomic_output(outfile) as tmp:
            dump(records, tmp, **encoder_kwargs)


def _redirect_stdout_to_devnull():
    """Redirect stdout's file descriptor so interpreter shutdown cannot flush a broken pipe."""

    with contextlib.suppress(AttributeError, OSError, ValueError):
        devnull = os.open(os.devnull, os.O_WRONLY)
        try:
            os.dup2(devnull, sys.stdout.fileno())
        finally:
            os.close(devnull)


def _is_broken_stdout(exc, outfile, /):
    """Return whether an output error represents a closed stdout pipe."""

    return outfile is None and (
        isinstance(exc, BrokenPipeError) or (sys.platform == "win32" and exc.errno == errno.EINVAL)
    )


def _cli_same_file(infile, outfile, /):
    """Return True when the input and output paths refer to the same file."""

    if outfile is None or infile is None or infile == "-" or _looks_like_url(infile):
        return False
    infile = os.fspath(infile)
    outfile = os.fspath(outfile)
    try:
        # Most accurate when both exist: compares device/inode, so it also
        # catches hardlinks and different paths aliasing the same file.
        return os.path.samefile(infile, outfile)
    except OSError:
        # `samefile` requires both paths to exist; fall back to a resolved-path
        # comparison for the common case where the output does not exist yet.
        src = os.path.normcase(os.path.realpath(infile))
        dst = os.path.normcase(os.path.realpath(outfile))
        return src == dst


def _build_parser():
    parser = argparse.ArgumentParser(
        prog="jsonl",
        description="Stream, convert, compress, and validate JSON Lines data.",
    )
    parser.add_argument(
        "infile",
        nargs="?",
        default="-",
        help="input JSON Lines file, archive (zip or tar), or URL; reads from stdin when omitted or '-'",
    )
    parser.add_argument(
        "outfile",
        nargs="?",
        default=None,
        help="output file; writes to stdout when omitted (compression is chosen from the extension)",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="write records using the most compact representation",
    )
    parser.add_argument(
        "--sort-keys",
        dest="sort_keys",
        action="store_true",
        help="sort object keys alphabetically in the output",
    )
    parser.add_argument(
        "--ascii",
        dest="ensure_ascii",
        action="store_true",
        help="escape non-ASCII characters as \\uXXXX (default: emit raw UTF-8)",
    )
    parser.add_argument(
        "--member",
        metavar="PATTERN",
        default=None,
        help="select JSON Lines members from a supported archive (zip/tar) using a shell-style pattern",
    )
    parser.add_argument(
        "--broken",
        action="store_true",
        help="skip invalid JSON records instead of aborting; exits 1 if any record was skipped",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (py-jsonl {})".format(_get_version()),
    )
    return parser


def _is_archive_path(path, /):
    """Return True if `path` is a readable zip or tar archive (which needs --member)."""

    if not isinstance(path, str) or not os.path.isfile(path):
        return False
    with contextlib.suppress(OSError):
        if zipfile.is_zipfile(path):
            return True
    with contextlib.suppress(OSError, tarfile.TarError):
        return tarfile.is_tarfile(path)
    return False


def main(argv=None):
    """Command-line entry point. Returns a process exit code."""

    parser = _build_parser()
    args = parser.parse_args(argv)
    infile = args.infile
    outfile = args.outfile

    # Configuration errors -> exit code 2 (argparse convention).
    if args.member is not None and (infile is None or infile == "-"):
        parser.error("--member requires an input archive file or URL, not stdin")
    if _cli_same_file(infile, outfile):
        parser.error("input and output must not refer to the same file")

    encoder_kwargs = {"ensure_ascii": args.ensure_ascii}
    if args.sort_keys:
        encoder_kwargs["sort_keys"] = True
    if args.compact:
        encoder_kwargs["separators"] = (",", ":")

    reporter = _BrokenRecordReporter()
    exit_code = _EXIT_OK
    try:
        records = _cli_records(infile, args.broken, args.member, reporter)
        _cli_write(records, outfile, encoder_kwargs)
    except (json.JSONDecodeError, UnicodeDecodeError):
        # Recoverable parsing error without --broken: the reporter already described it.
        exit_code = _EXIT_INVALID_RECORD
    except OSError as exc:
        # A downstream consumer closed early (e.g. `jsonl big.jsonl | head`).
        # Windows can report a closed stdout pipe as EINVAL rather than BrokenPipeError.
        if _is_broken_stdout(exc, outfile):
            _redirect_stdout_to_devnull()
            return _EXIT_RUNTIME_ERROR
        print("jsonl: error: {}".format(exc), file=sys.stderr)
        exit_code = _EXIT_RUNTIME_ERROR
    except Exception as exc:
        print("jsonl: error: {}".format(exc), file=sys.stderr)
        exit_code = _EXIT_RUNTIME_ERROR

    if outfile is None:
        try:
            sys.stdout.flush()
        except OSError as exc:
            if _is_broken_stdout(exc, outfile):
                _redirect_stdout_to_devnull()
            else:
                print("jsonl: error: {}".format(exc), file=sys.stderr)
            return _EXIT_RUNTIME_ERROR

    if exit_code == _EXIT_OK and args.broken and reporter.count:
        return _EXIT_INVALID_RECORD
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
