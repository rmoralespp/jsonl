# -*- coding: utf-8 -*-

import contextlib
import io
import os
import tempfile

import pytest

import jsonl
import tests


def test_dump_given_empty_string_io():
    with contextlib.closing(io.StringIO()) as fp:
        jsonl.dump((), fp)
        assert fp.getvalue() == ""


def test_dump_given_empty_bytes_io():
    with contextlib.closing(io.BytesIO()) as fp:
        jsonl.dump((), fp, text_mode=False)
        assert fp.getvalue() == b""


def test_dump_given_string_io():
    with contextlib.closing(io.StringIO()) as fp:
        jsonl.dump(iter(tests.data), fp)
        assert fp.getvalue() == tests.string_data


def test_dump_given_bytes_io():
    expected = tests.string_data.encode(jsonl.utf_8)
    with contextlib.closing(io.BytesIO()) as fp:
        jsonl.dump(iter(tests.data), fp, text_mode=False)
        assert fp.getvalue() == expected


@pytest.mark.parametrize(
    "mode, text_mode", (("wt", True), ("wb", False), ("ab", False), ("at", True))
)
@pytest.mark.parametrize("extension", tests.extensions)
def test_dump_given_file_object(extension, mode, text_mode):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, f"name{extension}")
        with jsonl.xopen(path, mode=mode) as fp:
            jsonl.dump(iter(tests.data), fp, text_mode=text_mode)
        result = tests.read_text(path)
        assert result == tests.string_data


def test_dump_given_invalid_file_object():
    with pytest.raises(ValueError):
        jsonl.dump(iter(tests.data), object())


@pytest.mark.parametrize("extension", tests.extensions)
def test_dump_given_filepath(extension):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, f"foo{extension}")
        jsonl.dump(iter(tests.data), path)
        result = tests.read_text(path)
    assert result == tests.string_data


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
