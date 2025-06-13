
import json
import os
import tempfile

import orjson
import pytest
import ujson


@pytest.fixture(scope="package", params=(True, False))
def broken(request):
    return request.param


@pytest.fixture(scope="package", params=(".jsonl", ".gz", ".bz2", ".xz", ".unknown"))
def file_extension(request):
    return request.param


@pytest.fixture(scope="package")
def filename(file_extension):
    return "filename" + file_extension


@pytest.fixture(scope="function")
def filepath(filename):
    with tempfile.TemporaryDirectory() as tmp:
        yield os.path.join(tmp, filename)


@pytest.fixture(scope="package", params=(orjson.loads, ujson.loads, json.loads, None))
def json_loads(request):
    return request.param
