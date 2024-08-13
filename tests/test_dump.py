# -*- coding: utf-8 -*-

import io

import jsonl


def test_dump_empty():
    fp = io.StringIO()
    jsonl.dump((), fp)
    result = fp.getvalue()
    assert result == ""


def test_dump_iter():
    value = iter(({"foo": 1}, {"ño": 2}))
    expected = '{"foo": 1}\n{"ño": 2}\n'
    fp = io.StringIO()
    jsonl.dump(value, fp)
    result = fp.getvalue()
    assert result == expected
