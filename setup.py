# -*- coding: utf-8 -*-

import setuptools

import jsonl


def read(filename):
    with open(filename, encoding="utf-8") as f:
        return f.read()


setuptools.setup(
    name=jsonl.__title__,
    version=jsonl.__version__,
    description="A simple Python library for handling jsonlines files.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet",
        "Topic :: Utilities",
        "Topic :: File Formats :: JSON",
    ],
    keywords=["jsonlines", "ndjson", "jsonl"],
    author="rmoralespp",
    author_email="rmoralespp@gmail.com",
    url="https://github.com/rmoralespp/jsonl",
    license="MIT",
    py_modules=["jsonl"],
    zip_safe=False,  # https://mypy.readthedocs.io/en/latest/installed_packages.html
    python_requires=">=3.8",
)
