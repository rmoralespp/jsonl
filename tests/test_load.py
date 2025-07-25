import contextlib
import io
import json
import os
import pathlib
import tempfile
import unittest.mock
import urllib.request

import pytest

import jsonl
import tests


def test_invalid_json_lines(broken):
    lines = (
        "prefix\n"  # bad JSON line
        "[1, 2]\n\n"  # multiple new lines
        "[3]\n"
        "affix\n"  # bad JSON line
        "[4]\n"
        "suffix\n"  # bad JSON line
    )
    with contextlib.closing(io.StringIO(lines)) as iofile:
        result = jsonl.load(iofile, broken=broken)
        if broken:
            assert tuple(result) == ([1, 2], [3], [4])
        else:
            with pytest.raises(json.JSONDecodeError):
                tests.consume(result)


def test_invalid_utf8(broken):
    with contextlib.closing(io.BytesIO(b"\xff\xff\n[1, 2]")) as iofile:
        result = jsonl.load(iofile, broken=broken)
        if broken:
            assert tuple(result) == ([1, 2],)
        else:
            with pytest.raises(UnicodeDecodeError):
                tests.consume(result)


@pytest.mark.parametrize(
    "iofile",
    [
        io.StringIO(tests.string_data),
        io.BytesIO(tests.string_data.encode(jsonl._utf_8)),
    ],
)
def test_memory_file(iofile):
    with contextlib.closing(iofile):
        result = tuple(jsonl.load(iofile))
    assert result == tuple(tests.data)


@pytest.mark.parametrize("mode", ("rt", "rb"))
def test_opened_file(filepath, mode, json_loads):
    expected = tuple(tests.data)
    # Prepare a file with JSON lines
    with jsonl._xopen(filepath, mode="wb") as fp:  # write into a binary file
        content = tests.string_data.encode(jsonl._utf_8)
        fp.write(content)
    # Load the file in given mode
    with jsonl._xopen(filepath, mode=mode) as fp:
        result = tuple(jsonl.load(fp, json_loads=json_loads))
    assert result == expected


@pytest.mark.parametrize("pathlike", (True, False))
def test_filepath(filepath, json_loads, pathlike):
    filepath = pathlib.Path(filepath) if pathlike else filepath
    expected = tuple(tests.data)
    tests.write_text(filepath, content=tests.string_data)
    result = tuple(jsonl.load(filepath, json_loads=json_loads))
    assert result == expected


@pytest.mark.parametrize("opener", (open, None))
def test_filepath_using_opener(opener):
    expected = tuple(tests.data)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "foo")
        tests.write_text(os.path.join(tmp, "foo"), content=tests.string_data)
        result = tuple(jsonl.load(path, opener=opener))
    assert result == expected


def test_filepath_not_found():
    with pytest.raises(FileNotFoundError):
        tests.consume(jsonl.load("not_found.jsonl"))


def test_url_using_opener():
    with pytest.raises(ValueError):
        next(jsonl.load("http://foo.com", opener=object()))


@pytest.mark.parametrize("charset", ("utf-8", "utf-16"))
@pytest.mark.parametrize("url_class", (urllib.request.Request, str))
@unittest.mock.patch("urllib.request.urlopen")
def test_url(urlopen, url_class, charset):
    fd = io.BytesIO(tests.string_data.encode(charset))
    fd.headers = unittest.mock.MagicMock()
    fd.headers.get_content_charset.return_value = charset
    urlopen.return_value.__enter__.return_value = fd

    result = tuple(jsonl.load(url_class("http://example.com/data.jsonl")))
    expected = tuple(tests.data)

    assert result == expected
