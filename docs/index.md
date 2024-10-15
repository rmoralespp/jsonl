# jsonl

[![CI](https://github.com/rmoralespp/jsonl/workflows/CI/badge.svg)](https://github.com/rmoralespp/jsonl/actions?query=event%3Arelease+workflow%3ACI)
[![pypi](https://img.shields.io/pypi/v/py-jsonl.svg)](https://pypi.python.org/pypi/py-jsonl)
[![versions](https://img.shields.io/pypi/pyversions/py-jsonl.svg)](https://github.com/rmoralespp/jsonl)
[![codecov](https://codecov.io/gh/rmoralespp/jsonl/branch/main/graph/badge.svg)](https://app.codecov.io/gh/rmoralespp/jsonl)
[![license](https://img.shields.io/github/license/rmoralespp/jsonl.svg)](https://github.com/rmoralespp/jsonl/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: ruff](https://img.shields.io/badge/linter-_ruff-orange)](https://github.com/charliermarsh/ruff)

## About

**jsonl** is a library that includes useful tools for working with jsonlines data as
described [jsonlines](https://jsonlines.org/)

**Features:**

- 🌎 Offers an API similar to Python's standard `json` module.
- 🚀 Supports custom serialization/deserialization callbacks. By default, it uses the standard `json` module.
- 🗜️ Enables compression/decompression using `gzip`, `bzip2`, and `xz` formats.
- 🔧 Load files containing broken lines, skipping any malformed lines.
- 📦 Provides a simple API for incremental writing to multiple files.

## Installation (via pip)

```pip install py-jsonl```
