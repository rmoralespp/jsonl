# -*- coding: utf-8 -*-

import logging
import os
import tempfile

import requests

import jsonl

headers = {"Content-Type": "application/jsonl"}
url = "http://127.0.0.1:5000/"


def fetch(count):
    for i in range(count):
        yield {"id": i, "title": "One Hundred Years of Solitude", "author": "García Márquez"}


def read_jsonl_stream(count):
    response = requests.get(url + f"api/data/{count}", headers=headers, stream=True)
    for item in jsonl.loader(response.iter_lines()):
        logging.debug("read_jsonl_stream: %s", item)


def write_jsonl_stream(count):
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "data.jsonl")
        jsonl.dump(fetch(count), path)

        with open(path, mode="rb") as fn:
            response = requests.post(url + "api/data/", data=fn, headers=headers, stream=True)

        for item in response.iter_lines():
            logging.debug("write_jsonl_stream: %s", item)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    read_jsonl_stream(10000)
    write_jsonl_stream(10000)
