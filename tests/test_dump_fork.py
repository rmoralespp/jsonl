# -*- coding: utf-8 -*-

import os
import tempfile

import pytest

import jsonl
import tests


@pytest.mark.parametrize("extension", jsonl.extensions)
def test_dump_fork_iter_data(extension):
    with tempfile.TemporaryDirectory() as tmp:
        foo_path = os.path.join(tmp, f"foo{extension}")
        var_path = os.path.join(tmp, f"var{extension}")
        baz_path = os.path.join(tmp, f"baz{extension}")

        path_items = (
            (foo_path, iter(({"foo": 1}, {"ño": 2}))),
            (foo_path, iter(({"extra": True},))),
            (var_path, iter(({"foo": 1}, {"ño": 2}))),
            (baz_path, iter(())),
        )
        jsonl.dump_fork(iter(path_items))

        assert tests.read_text(foo_path) == '{"foo": 1}\n{"ño": 2}\n{"extra": true}'
        assert tests.read_text(var_path) == '{"foo": 1}\n{"ño": 2}'
        assert tests.read_text(baz_path) == ""


@pytest.mark.parametrize("dump_if_empty", (True, False))
def test_dump_fork_empty_data(dump_if_empty):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "foo.jsonl")
        path_items = ((path, ()),)
        jsonl.dump_fork(iter(path_items), dump_if_empty=dump_if_empty)
        if dump_if_empty:
            assert tests.read_text(path) == ""
        else:
            assert not os.path.exists(path)
