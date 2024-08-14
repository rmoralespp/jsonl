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


def test_invalid_utf8():
    result = jsonl.load(io.BytesIO(b"\xff\xff"))
    with pytest.raises(UnicodeDecodeError):
        tests.consume(result)


def test_load_empty():
    result = jsonl.load(io.StringIO())
    assert tuple(result) == ()


def test_load_data():
    result = jsonl.load(io.StringIO(tests.string_data))
    assert tuple(result) == tuple(tests.data)
