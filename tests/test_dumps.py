# -*- coding: utf-8 -*-

import jsonl
import tests


def test_dumps_empty():
    assert not jsonl.dumps(())


def test_dumps_iter_data():
    result = jsonl.dumps(iter(tests.data))
    assert result == tests.string_data
