# -*- coding: utf-8 -*-

import jsonl


def test_empty():
    expected = ()
    result = jsonl.dumper(())
    assert tuple(result) == expected


def test_text_mode_true():
    value = iter(({"foo": 1}, {"ño": 2}))
    expected = ('{"foo": 1}\n', '{"ño": 2}\n')
    result = jsonl.dumper(value, text_mode=True)
    assert tuple(result) == expected


def test_text_mode_false():
    value = iter(({"foo": 1}, {"ño": 2}))
    expected = (b'{"foo": 1}\n', b'{"\xc3\xb1o": 2}\n')
    result = jsonl.dumper(value, text_mode=False)
    assert tuple(result) == expected
