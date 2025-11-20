# -*- coding: utf-8 -*-

import contextlib
import functools
import http.server
import json
import logging
import os
import pathlib
import tempfile
import threading

import orjson
import pytest
import ujson

import jsonl

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))


@contextlib.contextmanager
def manage_http_server(directory):
    """
    Context manager to run a simple HTTP server in a separate thread.
    Yields the base URI of the server.

    The server serves files from the specified directory.
    """

    class MyHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, fmt, *args):  # pragma: no cover
            # Overwrite to silence requests
            pass

    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0),
        functools.partial(MyHandler, directory=os.path.abspath(directory)),
    )
    name, port = server.socket.getsockname()
    url = "http://{}:{}/".format(name, port)

    server_thread = threading.Thread(target=server.serve_forever, name="http_server")
    server_thread.start()

    logging.debug("Serving: %s", directory)
    with server:  # Ensure server socket and request threads are properly closed
        try:
            yield url
        finally:
            server.shutdown()  # signal server_thread to exit
            server_thread.join()


@pytest.fixture(scope="session")
def http_server():
    with manage_http_server(DATA_DIR) as url:
        yield url


@pytest.fixture(scope="package", params=(True, False))
def broken(request):
    return request.param


@pytest.fixture(scope="package", params=(True, False))
def pathlike(request):
    return request.param


@pytest.fixture(scope="package", params=jsonl.extensions)
def file_extension(request):
    return request.param


@pytest.fixture(scope="package", params=(".zip", ".tar", ".tar.gz", ".tar.xz", ".tar.bz2",))
def archive_extension(request):
    return request.param


@pytest.fixture(scope="package")
def filename(file_extension):
    return "filename" + file_extension


@pytest.fixture
def tmp_dir():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pathlib.Path(tmp_dir)


@pytest.fixture
def filepath(tmp_dir, filename):
    return str(tmp_dir / filename)


@pytest.fixture(scope="package", params=(orjson.loads, ujson.loads, json.loads, None))
def json_loads(request):
    return request.param
