# -*- coding: utf-8 -*-

import contextlib
import io
import json
import os
import tempfile

import orjson
import pytest
import ujson

import jsonl
import tests


def test_dump_given_string_io():
    with contextlib.closing(io.StringIO()) as fp:
        jsonl.dump(iter(tests.data), fp)
        assert fp.getvalue() == tests.string_data


def test_dump_given_bytes_io():
    expected = tests.string_data.encode(jsonl.utf_8)
    with contextlib.closing(io.BytesIO()) as fp:
        jsonl.dump(iter(tests.data), fp, text_mode=False)
        assert fp.getvalue() == expected


@pytest.mark.parametrize("mode, text", (("wt", True), ("wb", False), ("ab", False), ("at", True)))
def test_dump_given_opened_file(filepath, mode, text):
    with jsonl.xopen(filepath, mode=mode) as fp:
        jsonl.dump(iter(tests.data), fp, text_mode=text)
    result = tests.read_text(filepath)
    assert result == tests.string_data


def test_dump_given_invalid_object():
    with pytest.raises(ValueError):
        jsonl.dump(iter(tests.data), object())


@pytest.mark.parametrize(
    "json_dumps, json_dumps_kwargs, expected",
    [
        (orjson.dumps, dict(), tests.compacted_string_data),
        (ujson.dumps, dict(ensure_ascii=False), tests.compacted_string_data),
        (json.dumps, dict(ensure_ascii=False), tests.string_data),
        (None, dict(), tests.string_data),
    ],
)
def test_dump_given_filepath(filepath, json_dumps, json_dumps_kwargs, expected):
    jsonl.dump(iter(tests.data), filepath, json_dumps=json_dumps, **json_dumps_kwargs)
    result = tests.read_text(filepath)
    assert result == expected


def test_dump_given_filepath_extension_with_opener():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "foo")
        jsonl.dump(iter(tests.data), path, opener=open)
        result = tests.read_text(path)
    assert result == tests.string_data


def test_dump_given_custom_file_write_method():
    class CustomFile:
        def __init__(self):
            self.content = ""

        def write(self, line):
            self.content += line

    file = CustomFile()
    jsonl.dump(tests.data, file)
    assert file.content == tests.string_data


def test_dump_given_custom_file_writelines_method():
    class CustomFile:
        def __init__(self):
            self.content = None

        def writelines(self, lines):
            self.content = "".join(lines)

    file = CustomFile()
    jsonl.dump(tests.data, file)
    assert file.content == tests.string_data
