# -*- coding: utf-8 -*-

import pytest

import jsonl


@pytest.mark.parametrize("mode, expected", [("wt", "utf-8"), ("wb", None), ("at", "utf-8")])
def test_get_encoding(mode, expected):
    assert jsonl.get_encoding(mode) == expected


@pytest.mark.parametrize(
    "value, text_mode, expected",
    [
        ("test", True, "test\n"),
        (b"test", True, "test\n"),
        ("test", False, b"test\n"),
        (b"test", False, b"test\n"),
    ],
)
def test_get_line(value, text_mode, expected):
    assert jsonl.get_line(value, text_mode) == expected
