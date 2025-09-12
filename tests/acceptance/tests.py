# -*- coding: utf-8 -*-

import pytest

import jsonl
import tests


def test_load_file_from_url(http_server_uri):
    url = http_server_uri + "foo.jsonl"
    data = list(jsonl.load(url))
    assert data == tests.data


@pytest.mark.parametrize("filename", ("archive.zip", "archive.tar"))
def test_load_archive_from_url(http_server_uri, filename):
    url = http_server_uri + "/" + filename
    loaded = jsonl.load_archive(url)
    loaded = [(name, list(data)) for name, data in loaded]
    assert loaded == [('foo.jsonl', tests.data), ('var.jsonl', tests.data)]
