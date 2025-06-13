
import os
import pathlib
import tempfile

import pytest
import ujson

import jsonl
import tests


@pytest.mark.parametrize(
    "json_dumps, json_dumps_kwargs",
    [
        (ujson.dumps, {"ensure_ascii": False, "separators": (", ", ": ")}),
        (None, {}),
    ],
)
@pytest.mark.parametrize("text_mode", (True, False))
def test_iter_data(file_extension, text_mode, json_dumps, json_dumps_kwargs):
    with tempfile.TemporaryDirectory() as tmp:
        foo_path = os.path.join(tmp, f"foo{file_extension}")
        var_path = os.path.join(tmp, f"var{file_extension}")
        baz_path = os.path.join(tmp, f"baz{file_extension}")

        path_items = (
            (foo_path, iter(({"foo": 1}, {"ño": 2}))),
            (foo_path, iter(({"extra": True},))),
            (var_path, iter(({"foo": 1}, {"ño": 2}))),
            (baz_path, iter(())),
        )
        jsonl.dump_fork(iter(path_items), text_mode=text_mode, json_dumps=json_dumps, **json_dumps_kwargs)

        assert tests.read_text(foo_path) == '{"foo": 1}\n{"ño": 2}\n{"extra": true}\n'
        assert tests.read_text(var_path) == '{"foo": 1}\n{"ño": 2}\n'
        assert tests.read_text(baz_path) == ""


@pytest.mark.parametrize("pathlike", (True, False))
@pytest.mark.parametrize("dump_if_empty", (True, False))
def test_empty_data(filepath, dump_if_empty, pathlike):
    filepath = pathlib.Path(filepath) if pathlike else filepath
    path_items = ((filepath, ()),)
    jsonl.dump_fork(iter(path_items), dump_if_empty=dump_if_empty)
    if dump_if_empty:
        assert tests.read_text(filepath) == ""
    else:
        assert not os.path.exists(filepath)
