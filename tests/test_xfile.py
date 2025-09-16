# -*- coding: utf-8 -*-

import bz2
import gzip
import io
import lzma
import unittest.mock

import pytest

import jsonl
import tests


def test_xfile_object(filepath):
    obj = unittest.mock.MagicMock()  # subscribable object
    with jsonl._xfile(filepath, obj) as result:
        if filepath.endswith(".gz"):
            assert isinstance(result, gzip.GzipFile)
        elif filepath.endswith(".bz2"):
            assert isinstance(result, bz2.BZ2File)
        elif filepath.endswith(".xz"):
            assert isinstance(result, lzma.LZMAFile)
        else:
            assert result is obj


def test_xfile_close(filepath):
    buffer = io.BytesIO()

    with jsonl._xfile(filepath, buffer) as output:
        assert not output.closed
        assert not buffer.closed

    if buffer is output:
        # the output should not close the buffer because it is not responsible for closing it.
        assert not buffer.closed
    else:
        assert output.closed
        assert not buffer.closed


@pytest.mark.parametrize(
    "file_content, expected",
    [
        (b"\x1f\x8b\x08\x00\x00\x00", jsonl.ext_gz),  # Gzip signature
        (b"\x42\x5a\x68\x31\x31\x39", jsonl.ext_bz2),  # Bzip2 signature
        (b"\xfd\x37\x7a\x58\x5a\x00", jsonl.ext_xz),  # XZ signature
        (b"\x00\x00\x00\x00\x00\x00", None),  # No matching signature
        (b"", None),  # Empty file content
    ],
)
def test_get_fileobj_extension_ok(file_content, expected):
    fd = io.BytesIO(file_content)
    assert jsonl._get_fileobj_extension(fd) == expected


def test_get_fileobj_extension_restores_file_pointer():
    file_content = b"\x1f\x8b\x08\x00\x00\x00"
    fd = io.BytesIO(file_content)
    initial_position = fd.tell()
    jsonl._get_fileobj_extension(fd)
    assert fd.tell() == initial_position


@pytest.mark.parametrize(
    "name, mode, fileobj, expected",
    [
        # Known extensions
        ("file.jsonl", "r", None, jsonl.ext_jsonl),
        ("file.gz", "rb", io.BytesIO(b"\x1f\x8b"), jsonl.ext_gz),
        ("file.bz2", "rb", io.BytesIO(b"\x42\x5a\x68"), jsonl.ext_bz2),
        ("file.xz", "rb", io.BytesIO(b"\xfd\x37\x7a\x58\x5a\x00"), jsonl.ext_xz),
        # Unknown extensions but detected by signature
        ("file.unknown", "rb", io.BytesIO(b"\x1f\x8b"), jsonl.ext_gz),
        ("file.unknown", "rb", io.BytesIO(b"\x42\x5a\x68"), jsonl.ext_bz2),
        ("file.unknown", "rb", io.BytesIO(b"\xfd\x37\x7a\x58\x5a\x00"), jsonl.ext_xz),
        # Unknown extension but text mode
        ("file.unknown", "r", None, None),
        # Unknown extension but write/append binary mode
        ("file.unknown", "wb", None, None),
        # Unknown extensions and no fileobj or undetectable fileobj
        ("file", "r", None, None),  # No extension
        ("file", "rb", io.BytesIO(b""), None),  # No extension, empty fileobj
    ],
)
def test_get_file_extension_ok(name, mode, fileobj, expected, tmp_dir):
    path = tmp_dir / name
    if not fileobj:
        tests.write_text(path)
    assert jsonl._get_file_extension(path, mode, fileobj=fileobj) == expected


def test_get_file_extension_ko():
    with pytest.raises(FileNotFoundError):
        jsonl._get_file_extension("nonexistent.file", "r")
