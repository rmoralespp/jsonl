# jsonl

[![GitHub tag](https://img.shields.io/github/tag/rmoralespp/jsonl?include_prereleases=&sort=semver&color=black)](https://github.com/rmoralespp/jsonl/releases/)
[![CI](https://github.com/rmoralespp/jsonl/workflows/CI/badge.svg)](https://github.com/rmoralespp/jsonl/actions?query=event%3Arelease+workflow%3ACI)
[![pypi](https://img.shields.io/pypi/v/py-jsonl.svg)](https://pypi.python.org/pypi/py-jsonl)
[![versions](https://img.shields.io/pypi/pyversions/py-jsonl.svg)](https://github.com/rmoralespp/jsonl)
[![codecov](https://codecov.io/gh/rmoralespp/jsonl/branch/main/graph/badge.svg)](https://app.codecov.io/gh/rmoralespp/jsonl)
[![license](https://img.shields.io/github/license/rmoralespp/jsonl.svg)](https://github.com/rmoralespp/jsonl/blob/main/LICENSE)
[![Linter: ruff](https://img.shields.io/badge/linter-_ruff-orange)](https://github.com/charliermarsh/ruff)
[![Downloads](https://pepy.tech/badge/py-jsonl)](https://pepy.tech/project/py-jsonl)

---

## About

**jsonl** is a lightweight Python library designed to simplify working with JSON Lines data, adhering to
the [jsonlines](https://jsonlines.org/) and [ndjson](https://github.com/ndjson/ndjson-spec) specifications.

### 🎯 Features

- 🌎 Provides an API similar to Python's standard `json` module.
- 🚀 Supports custom (de)serialization via user-defined callbacks.
- 🗜️ Built-in support for `gzip`, `bzip2`, `xz` compression formats and `ZIP` or `TAR` archives.
- 🔧 Skips malformed lines during file loading.
- 📥 Loads from URLs directly.
- 🐍 No external dependencies: relies only on the Python standard library.

## 📦 Installation

To install **jsonl** using `pip`, run the following command:

```bash
pip install py-jsonl
```

## ⚡ Quick Start

**Dumping data to a JSON Lines File**

> [!NOTE]
>
> Use `jsonl.dump` to incrementally write an iterable of dictionaries to a JSON Lines file:

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "file.jsonl")
```

**Loading data from a JSON Lines source**

> [!NOTE]
>
> Use `jsonl.load` to incrementally load a JSON Lines source—such as a **filename, URL, or file-like object—into** as an
> iterator of dictionaries:

```python
import jsonl

# Load data from a JSON Lines file
iterator = jsonl.load("file.jsonl")
print(tuple(iterator))

# Load data from a URL
iterator = jsonl.load("https://example.com/file.jsonl")
print(tuple(iterator))
```

**Dump multiple JSON Lines Files into an Archive (ZIP or TAR)**

> [!NOTE]
>
> Use `jsonl.dump_archive` to incrementally write structured data to multiple JSON Lines files,
> which are then stored in a ZIP or TAR archive.

```python
# -*- coding: utf-8 -*-

import jsonl

data = [
    # Create `file1.jsonl` withing the archive
    ("file1.jsonl", [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]),
    # Create `file2.jsonl` within the archive
    ("path/to/file2.jsonl", [{"name": "Charlie", "age": 35}, {"name": "David", "age": 40}]),
    # Append to `file1.jsonl` within the archive
    ("file1.jsonl", [{"name": "Eve", "age": 28}]),
]
jsonl.dump_archive("archive.zip", data)
```

**Load multiple JSON Lines Files from an Archive (ZIP or TAR)**

> [!NOTE]
>
> Use `jsonl.load_archive` to incrementally load multiple JSON Lines files from a ZIP or TAR archive.

> [!TIP]
>
> - It is possible to load the archive from a URL
> - This function allows you to filter files using Unix shell-style wildcards.

```python
# -*- coding: utf-8 -*-

import jsonl

# Load all JSON Lines files matching the pattern "*.jsonl" from a local archive
for filename, iterator in jsonl.load_archive("archive.zip"):
    print("Filename:", filename)
    print("Data:", tuple(iterator))

# Load all JSON Lines files matching the pattern "*.jsonl" from a remote archive
for filename, iterator in jsonl.load_archive("https://example.com/archive.zip"):
    print("Filename:", filename)
    print("Data:", tuple(iterator))
```

**Dumping data to Multiple JSON Lines Files**

> [!NOTE]
>
> Use `jsonl.dump_fork` to incrementally write structured data to multiple JSON Lines files,
> which can be useful when you want to separate data based on some criteria.

```python
# -*- coding: utf-8 -*-

import jsonl

data = [
    # Create `file1.jsonl` or overwrite it if it exists
    ("file1.jsonl", [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]),
    # Create `file2.jsonl` or overwrite it if it exists
    ("file2.jsonl", [{"name": "Charlie", "age": 35}, {"name": "David", "age": 40}]),
    # Append to `file1.jsonl`
    ("file1.jsonl", [{"name": "Eve", "age": 28}]),
]
jsonl.dump_fork(data)
```

---

## 📚 Documentation

For more detailed information and usage examples, refer to the
project [documentation](https://rmoralespp.github.io/jsonl/)

## 🛠️ Development

To contribute to the project, you can run the following commands for testing and documentation:

First, ensure you have the latest version of `pip`:

```bash
python -m pip install --upgrade pip
```

### Running Unit Tests

Install the development dependencies and run the tests:

```bash
pip install --group=test  --upgrade # Install test dependencies, skip if already installed
python -m pytest tests/ # Run all tests
python -m pytest tests/ --cov # Run tests with coverage
```

### Running Linters

```bash
pip install --group=lint --upgrade  # Install lint dependencies, skip if already installed
ruff check . # Run linter
spxl . # Run sphinx-linter for docstring issues
pymport . # Check for import issues
```

### Building the Documentation

To build the documentation locally, use the following commands:

```bash
pip install --group=doc --upgrade  # Install doc dependencies, skip if already installed
mkdocs serve # Start live-reloading docs server
mkdocs build # Build the documentation site
```

## 🗒️ License

This project is licensed under the [MIT license](LICENSE).
