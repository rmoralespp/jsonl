# jsonl

[![CI](https://github.com/rmoralespp/jsonl/workflows/CI/badge.svg)](https://github.com/rmoralespp/jsonl/actions?query=event%3Arelease+workflow%3ACI)
[![pypi](https://img.shields.io/pypi/v/py-jsonl.svg)](https://pypi.python.org/pypi/py-jsonl)
[![versions](https://img.shields.io/pypi/pyversions/py-jsonl.svg)](https://github.com/rmoralespp/jsonl)
[![codecov](https://codecov.io/gh/rmoralespp/jsonl/branch/main/graph/badge.svg)](https://app.codecov.io/gh/rmoralespp/jsonl)
[![license](https://img.shields.io/github/license/rmoralespp/jsonl.svg)](https://github.com/rmoralespp/jsonl/blob/main/LICENSE)
[![Linter: ruff](https://img.shields.io/badge/linter-_ruff-orange)](https://github.com/charliermarsh/ruff)
[![Downloads](https://pepy.tech/badge/py-jsonl)](https://pepy.tech/project/py-jsonl)

## About

**jsonl** is a Python library designed to simplify working with JSON Lines data, adhering to
the [JSON Lines format](https://jsonlines.org/).

**Features:**

- 🌎 Provides an API similar to Python's standard `json` module.
- 🚀 Supports custom (de)serialization via user-defined callbacks.
- 🗜️ Built-in support for `gzip`, `bzip2`, `xz` compression formats and `ZIP` or `TAR` archives.
- 🔧 Skips malformed lines during file loading.
- 📥 Loads from URLs, file paths, or file-like objects.

## Installation (via pip)

```pip install py-jsonl```
