# -*- coding: utf-8 -*-

import jsonl


def test_dumps_empty():
    assert not jsonl.dumps(())


def test_dumps_data():
    expected = '{"ño": 1}\n{"foo": "var"}\n'
    value = ({"ño": 1}, {"foo": "var"})
    result = jsonl.dumps(iter(value))
    assert result == expected
