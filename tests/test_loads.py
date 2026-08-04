# -*- coding: utf-8 -*-
import collections
import json

import pytest

import jsonl
import tests


def test_empty():
    assert list(jsonl.loads("")) == []


def test_basic():
    result = list(jsonl.loads(tests.string_data))
    assert result == tests.data


def test_roundtrip():
    text = jsonl.dumps(tests.data)
    result = list(jsonl.loads(text))
    assert result == tests.data


def test_returns_iterator():
    result = jsonl.loads(tests.string_data)
    assert hasattr(result, "__next__")


def test_broken_skip():
    text = '{"a": 1}\ninvalid\n{"b": 2}\n'
    result = list(jsonl.loads(text, broken=True))
    assert result == [{"a": 1}, {"b": 2}]


def test_broken_raise():
    text = '{"a": 1}\ninvalid\n{"b": 2}\n'
    with pytest.raises(Exception):
        tests.consume(jsonl.loads(text, broken=False))


def test_custom_decoder_cls():
    result = list(jsonl.loads(tests.string_data, cls=json.JSONDecoder))
    assert result == tests.data
