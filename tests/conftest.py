import json
import pathlib
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


@pytest.fixture(scope="package", params=(".zip", ".tar", ".tar.gz", ".tar.xz", ".tar.bz2",))
def archive_extension(request):
    return request.param


@pytest.fixture(scope="package")
def filename(file_extension):
    return "filename" + file_extension


@pytest.fixture()
def tmp_dir():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pathlib.Path(tmp_dir)


@pytest.fixture(scope="function")
def filepath(tmp_dir, filename):
    yield str(tmp_dir / filename)


@pytest.fixture(scope="package", params=(orjson.loads, ujson.loads, json.loads, None))
def json_loads(request):
    return request.param
