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
        tests.write(path)
        result = tuple(jsonl.load_from(path))
    assert result == expected


def test_load_data():
    value = '{"foo": 1}\n{"ño": 2}\n'
    expected = ({"foo": 1}, {"ño": 2})

    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "foo.jsonl")
        tests.write(path, value)
        result = tuple(jsonl.load_from(path))

    assert result == expected


def test_file_not_found():
    with pytest.raises(FileNotFoundError):
        tests.consume(jsonl.load_from("jsonl.json"))
