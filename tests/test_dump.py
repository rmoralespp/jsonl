
import contextlib
import io
import json
import os
import pathlib
import tempfile

import orjson
import pytest
import ujson

import jsonl
import tests


def test_string_io():
    with contextlib.closing(io.StringIO()) as fp:
        jsonl.dump(iter(tests.data), fp)
        assert fp.getvalue() == tests.string_data


def test_bytes_io():
    expected = tests.string_data.encode(jsonl._utf_8)
    with contextlib.closing(io.BytesIO()) as fp:
        jsonl.dump(iter(tests.data), fp, text_mode=False)
        assert fp.getvalue() == expected


@pytest.mark.parametrize("mode, text", (("wt", True), ("wb", False), ("ab", False), ("at", True)))
def test_opened_file(filepath, mode, text):
    with jsonl._xopen(filepath, mode=mode) as fp:
        jsonl.dump(iter(tests.data), fp, text_mode=text)
    result = tests.read_text(filepath)
    assert result == tests.string_data


def test_invalid_object():
    with pytest.raises(ValueError):
        jsonl.dump(iter(tests.data), object())


@pytest.mark.parametrize("pathlike", (True, False))
@pytest.mark.parametrize(
    "json_dumps, json_dumps_kwargs, expected",
    [
        (orjson.dumps, {}, tests.compacted_string_data),
        (ujson.dumps, {"ensure_ascii": False}, tests.compacted_string_data),
        (json.dumps, {"ensure_ascii": False}, tests.string_data),
        (None, {}, tests.string_data),
    ],
)
def test_filepath(filepath, json_dumps, json_dumps_kwargs, expected, pathlike):
    filepath = pathlib.Path(filepath) if pathlike else filepath
    jsonl.dump(iter(tests.data), filepath, json_dumps=json_dumps, **json_dumps_kwargs)
    result = tests.read_text(filepath)
    assert result == expected


def test_filepath_without_extension_using_opener():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "foo")
        jsonl.dump(iter(tests.data), path, opener=open)
        result = tests.read_text(path)
    assert result == tests.string_data


def test_custom_file_write_method():
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
