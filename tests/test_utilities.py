import os.path
import sys
import urllib.request

import pytest

import jsonl


@pytest.mark.parametrize("mode, expected", [("wt", "utf-8"), ("wb", None), ("at", "utf-8")])
def test_get_encoding(mode, expected):
    assert jsonl._get_encoding(mode) == expected


@pytest.mark.parametrize(
    "value, text_mode, expected",
    [
        ("test", True, "test\n"),
        (b"test", True, "test\n"),
        ("test", False, b"test\n"),
        (b"test", False, b"test\n"),
    ],
)
def test_get_line(value, text_mode, expected):
    assert jsonl._get_line(value, text_mode) == expected


@pytest.mark.parametrize("filename, expected", [
    ("foo.zip", "zip"),
    ("foo.tar", "tar"),
    ("foo.tar.gz", "gztar"),
    ("foo.tar.bz2", "bztar"),
    ("foo.tar.xz", "xztar"),
])
def test_get_archive_format(filename, expected):
    assert jsonl._get_archive_format(filename) == expected


@pytest.mark.parametrize("filename, expected", [
    ("path/to/foo.zip", os.path.join("path", "to", "foo")),
    ("path/to/foo.tar", os.path.join("path", "to", "foo")),
    ("path/to/foo.tar.gz", os.path.join("path", "to", "foo")),
    ("path/to/foo.tar.bz2", os.path.join("path", "to", "foo")),
    ("path/to/foo.tar.xz", os.path.join("path", "to", "foo")),
    ("path/to.var/foo.var.tar.xz", os.path.join("path", "to.var", "foo")),
    ("foo.zip", "foo"),
    ("foo.tar", "foo"),
    ("foo.tar.gz", "foo"),
    ("foo.tar.bz2", "foo"),
    ("foo.tar.xz", "foo"),
])
def test_del_archive_extension(filename, expected):
    assert jsonl._del_archive_extension(filename) == expected


@pytest.mark.parametrize("ext", [
    "",  # empty
    "foo",  # no extension
    "foo.invalid",  # unsupported extension
    "foo.gz",  # non-tar gzip
    "foo.xz",  # non-tar xz
    "foo.bz2",  # non-tar bzip2
    "foo.var.tar.gz",  # tar with extra extensions
    "foo.var.tar.bz2",  # tar with extra extensions
    "foo.var.tar.xz",  # tar with extra extensions
    "foo.TAR",  # case-insensitive check
])
def test_get_archive_format_invalid(ext):
    with pytest.raises(ValueError, match=f"Unsupported archive extension: {ext}"):
        jsonl._get_archive_format(ext)


@pytest.mark.parametrize("url, expected", [
    ("http://example.com", True),
    (urllib.request.Request("http://example.com"), True),  # Request object
    ("file:///path/to/data.jsonl", True),
])
def test_looks_like_url(url, expected):
    assert jsonl._looks_like_url(url) == expected


def test_looks_like_url_filepath():
    expected = sys.platform != "win32"
    assert jsonl._looks_like_url("D:/path/to/data.jsonl") == expected
