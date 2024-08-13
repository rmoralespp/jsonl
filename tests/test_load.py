# -*- coding: utf-8 -*-

import io
import json

import pytest

import jsonl
import tests


def test_invalid_lines():
    result = jsonl.load(io.StringIO("[1, 2]\n\n[3]"))
    with pytest.raises(json.JSONDecodeError):
        tests.consume(result)


def test_invalid_utf8() -> None:
    result = jsonl.load(io.BytesIO(b"\xff\xff"))
    with pytest.raises(UnicodeDecodeError):
        tests.consume(result)


def test_load_empty():
    result = jsonl.load(io.StringIO())
    assert tuple(result) == ()


def test_load_data():
    value = '{"foo": 1}\n{"ño": 2}\n'
    expected = ({"foo": 1}, {"ño": 2})
    result = jsonl.load(io.StringIO(value))
    assert tuple(result) == expected
