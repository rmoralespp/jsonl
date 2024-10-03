# -*- coding: utf-8 -*-

import contextlib
import io
import json
import os
import tempfile

import pytest

import jsonl
import tests


def test_load_given_invalid_json_lines(broken):
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


def test_load_given_invalid_utf8(broken):
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
        io.BytesIO(tests.string_data.encode(jsonl.utf_8)),
    ],
)
def test_load_given_memory_file(iofile):
    with contextlib.closing(iofile):
        result = tuple(jsonl.load(iofile))
    assert result == tuple(tests.data)


@pytest.mark.parametrize("mode", ("rt", "rb"))
def test_load_given_opened_file(filepath, mode, json_loads):
    expected = tuple(tests.data)
    # Prepare a file with JSON lines
    with jsonl.xopen(filepath, mode="wb") as fp:  # write into a binary file
        content = tests.string_data.encode(jsonl.utf_8)
        fp.write(content)
    # Load the file in given mode
    with jsonl.xopen(filepath, mode=mode) as fp:
        result = tuple(jsonl.load(fp, json_loads=json_loads))
    assert result == expected


def test_load_given_filepath(filepath, json_loads):
    expected = tuple(tests.data)
    tests.write_text(filepath, content=tests.string_data)
    result = tuple(jsonl.load(filepath, json_loads=json_loads))
    assert result == expected


@pytest.mark.parametrize("opener", (open, None))
def test_load_given_filepath_on_opener(opener):
    expected = tuple(tests.data)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "foo")
        tests.write_text(os.path.join(tmp, "foo"), content=tests.string_data)
        result = tuple(jsonl.load(path, opener=opener))
    assert result == expected


def test_load_given_not_found_filepath():
    with pytest.raises(FileNotFoundError):
        tests.consume(jsonl.load("not_found.jsonl"))
