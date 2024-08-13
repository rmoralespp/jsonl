# -*- coding: utf-8 -*-

import jsonl


def test_empty():
    expected = ()
    result = jsonl.dumper(())
    assert tuple(result) == expected


def test_no_empty():
    value = iter(({"foo": 1}, {"ño": 2}))
    expected = ('{"foo": 1}', "\n", '{"ño": 2}', "\n")
    result = jsonl.dumper(value)
    assert tuple(result) == expected
