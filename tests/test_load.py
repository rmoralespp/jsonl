# -*- coding: utf-8 -*-

import contextlib
import io
import json
import os
import tempfile

import pytest

import jsonl
import tests


@pytest.mark.parametrize("broken", (False, True))
def test_load_given_invalid_json_lines(broken):
    lines = (
        "prefix\n"  # bad JSON line
        "[1, 2]\n\n"  # multiple new lines
        "[3]\n"
        "affix\n"  # bad JSON line
        "[4]\n"
        "suffix\n"  # bad JSON line
    )
    result = jsonl.load(io.StringIO(lines), broken=broken)
    if broken:
        assert tuple(result) == ([1, 2], [3], [4])
    else:
        with pytest.raises(json.JSONDecodeError):
            tests.consume(result)


@pytest.mark.parametrize("broken", (False, True))
def test_load_given_invalid_utf8(broken):
    result = jsonl.load(io.BytesIO(b"\xff\xff\n[1, 2]"), broken=broken)
    if broken:
        assert tuple(result) == ([1, 2],)
    else:
        with pytest.raises(UnicodeDecodeError):
            tests.consume(result)


@pytest.mark.parametrize("iofile", (io.StringIO(), io.BytesIO()))
def test_load_give_empty_iofile(iofile):
    with contextlib.closing(iofile):
        result = tuple(jsonl.load(iofile))
    assert result == ()


@pytest.mark.parametrize(
    "iofile",
    (io.StringIO(tests.string_data), io.BytesIO(tests.string_data.encode(jsonl.utf_8))),
)
def test_load_given_iofile(iofile):
    with contextlib.closing(iofile):
        result = tuple(jsonl.load(iofile))
    assert result == tuple(tests.data)


@pytest.mark.parametrize("mode", ("rt", "rb"))
@pytest.mark.parametrize("extension", tests.extensions)
def test_load_given_file_like_object(extension, mode):
    expected = tuple(tests.data)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, f"foo.{extension}")
        with jsonl.xopen(path, mode="wb") as fp:  # write into a binary file
            fp.write(tests.string_data.encode(jsonl.utf_8))

        with jsonl.xopen(path, mode=mode) as fp:
            result = tuple(jsonl.load(fp))
    assert result == expected


@pytest.mark.parametrize("extension", tests.extensions)
def test_load_given_filepath(extension):
    expected = tuple(tests.data)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, f"foo{extension}")
        tests.write_text(path, content=tests.string_data)
        result = tuple(jsonl.load(path))
    assert result == expected


@pytest.mark.parametrize("opener", (open, None))
def test_load_given_filepath_and_opener(opener):
    expected = tuple(tests.data)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "foo")
        tests.write_text(os.path.join(tmp, "foo"), content=tests.string_data)
        result = tuple(jsonl.load(path, opener=opener))
    assert result == expected


def test_load_given_not_found_filepath():
    with pytest.raises(FileNotFoundError):
        tests.consume(jsonl.load("foo.jsonl"))
