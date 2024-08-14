# -*- coding: utf-8 -*-

import io

import jsonl
import tests


def test_dump_empty():
    fp = io.StringIO()
    jsonl.dump((), fp)
    assert fp.getvalue() == ""


def test_dump_iter_data():
    fp = io.StringIO()
    jsonl.dump(iter(tests.data), fp)
    assert fp.getvalue() == tests.string_data
