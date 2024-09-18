# -*- coding: utf-8 -*-

import contextlib
import io
import json
import os
import tempfile

import pytest

import jsonl
import tests


def test_load_given_invalid_lines():
    result = jsonl.load(io.StringIO("[1, 2]\n\n[3]"))
    with pytest.raises(json.JSONDecodeError):
        tests.consume(result)


def test_load_given_invalid_utf8():
    result = jsonl.load(io.BytesIO(b"\xff\xff"))
    with pytest.raises(UnicodeDecodeError):
        tests.consume(result)


@pytest.mark.parametrize("iofile", (io.StringIO(), io.BytesIO()))
def test_load_give_empty_iofile(iofile):
    with contextlib.closing(iofile):
        result = tuple(jsonl.load(iofile))
    assert result == ()


@pytest.mark.parametrize(
    "iofile",
    (io.StringIO(tests.string_data), io.BytesIO(tests.string_data.encode("utf-8"))),
)
def test_load_given_iofile(iofile):
    with contextlib.closing(iofile):
        result = tuple(jsonl.load(iofile))
    assert result == tuple(tests.data)


@pytest.mark.parametrize("mode", ("rt", "rb"))
@pytest.mark.parametrize("extension", jsonl.extensions)
def test_load_given_file_like(extension, mode):
    expected = tuple(tests.data)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, f"foo.{extension}")
        with jsonl.xopen(path, mode="wb") as fp:  # write into a binary file
            fp.write(tests.string_data.encode(jsonl.utf_8))

        with jsonl.xopen(path, mode=mode) as fp:
            result = tuple(jsonl.load(fp))
    assert result == expected


@pytest.mark.parametrize("extension", jsonl.extensions)
def test_load_given_filepath(extension):
    expected = tuple(tests.data)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, f"foo{extension}")
        tests.write_text(path, content=tests.string_data)
        result = tuple(jsonl.load(path))
    assert result == expected


def test_load_given_not_found_filepath():
    with pytest.raises(FileNotFoundError):
        tests.consume(jsonl.load("foo.jsonl"))


def test_load_given_invalid_filepath_extension():
    with pytest.raises(ValueError):
        tests.consume(jsonl.load("foo.other"))
