# -*- coding: utf-8 -*-

import os
import tempfile

import pytest

import jsonl
import tests


def test_load_empty():
    expected = ()
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "foo.jsonl")
        tests.write_text(path)
        result = tuple(jsonl.load_from(path))
    assert result == expected


@pytest.mark.parametrize("extension", ("jsonl.gzip", "jsonl.gz", "jsonl"))
def test_load_data(extension):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, f"foo.{extension}")
        tests.write_text(path, content=tests.string_data)
        result = tuple(jsonl.load_from(path))
    assert result == tuple(tests.data)


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        tests.consume(jsonl.load_from("jsonl.json"))
