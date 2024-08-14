# -*- coding: utf-8 -*-

import os
import tempfile

import pytest

import jsonl
import tests


def test_dump_into_exists_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "foo.jsonl")
        jsonl.dump_into(path, ())
        assert os.path.exists(path)


@pytest.mark.parametrize("extension", ("jsonl.gzip", "jsonl.gz", "jsonl"))
def test_dump_into_iter_data(extension):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "foo.{}".format(extension))
        jsonl.dump_into(path, iter(tests.data))
        result = tests.read_text(path)
    assert result == tests.string_data
