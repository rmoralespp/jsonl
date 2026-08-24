"""
Tests for the expression query helpers (`where` / `extract`).

These exercise both backends when available: the native ``aero-jsonl`` kernel
and the pure-Python ``jmespath`` fallback.
"""
import json

import pytest

import jsonl

DATA = [
    {"name": "x", "up": True, "load": 0.3},
    {"name": "y", "up": False, "load": 0.7},
    {"name": "z", "up": True, "load": 0.5},
]


@pytest.fixture
def src(tmp_path):
    path = tmp_path / "data.jsonl"
    path.write_text("".join(json.dumps(d) + "\n" for d in DATA), encoding="utf-8")
    return str(path)


def test_where_truthy_field(src):
    assert list(jsonl.where("up", src)) == [DATA[0], DATA[2]]


def test_where_comparison(src):
    assert list(jsonl.where("load > `0.4`", src)) == [DATA[1], DATA[2]]


def test_where_missing_field(src):
    assert list(jsonl.where("missing", src)) == []


def test_extract_field(src):
    assert list(jsonl.extract("name", src)) == ["x", "y", "z"]


def test_extract_null_skipped(src):
    assert list(jsonl.extract("missing", src)) == []


def test_extract_nested(src):
    assert list(jsonl.extract("`1`", src)) == [1, 1, 1]


def test_where_filelike(src):
    with open(src, encoding="utf-8") as f:
        assert list(jsonl.where("up", f)) == [DATA[0], DATA[2]]


def test_extract_string(src):
    assert list(jsonl.extract("name", src)) == ["x", "y", "z"]


def test_where_compressed(tmp_path):
    import gzip

    path = tmp_path / "data.jsonl.gz"
    with gzip.open(path, "wt", encoding="utf-8") as f:
        for d in DATA:
            f.write(json.dumps(d) + "\n")
    assert list(jsonl.where("up", str(path))) == [DATA[0], DATA[2]]


def test_no_engine_raises(monkeypatch):
    monkeypatch.setattr(jsonl, "_aero", None)
    monkeypatch.setattr(jsonl, "_jmespath", None)
    with pytest.raises(ImportError):
        list(jsonl.where("up", '{"up": true}'))
