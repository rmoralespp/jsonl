# -*- coding: utf-8 -*-

import os
import tempfile

import jsonl


def test_exists_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "foo.jsonl")
        jsonl.dump_into(path, ())
        assert os.path.exists(path)


def test_dumped_iter_data():
    value = iter(({"foo": 1}, {"ño": 2}))
    expected = '{"foo": 1}\n{"ño": 2}\n'
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "foo.jsonl")
        jsonl.dump_into(path, value)
        with open(path, encoding="utf-8") as f:
            result = f.read()
    assert result == expected
