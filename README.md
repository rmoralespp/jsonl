# jsonl

[![CI](https://github.com/rmoralespp/jsonl/workflows/CI/badge.svg)](https://github.com/rmoralespp/jsonl/actions?query=event%3Arelease+workflow%3ACI)
[![pypi](https://img.shields.io/pypi/v/py-jsonl.svg)](https://pypi.python.org/pypi/py-jsonl)
[![versions](https://img.shields.io/pypi/pyversions/py-jsonl.svg)](https://github.com/rmoralespp/jsonl)
[![codecov](https://codecov.io/gh/rmoralespp/jsonl/branch/main/graph/badge.svg)](https://app.codecov.io/gh/rmoralespp/jsonl)
[![license](https://img.shields.io/github/license/rmoralespp/jsonl.svg)](https://github.com/rmoralespp/jsonl/blob/main/LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linter: ruff](https://img.shields.io/badge/linter-_ruff-orange)](https://github.com/charliermarsh/ruff)
[![Downloads](https://pepy.tech/badge/py-jsonl)](https://pepy.tech/project/py-jsonl)

## About

**jsonl** is a Python library designed to simplify working with JSON Lines data, adhering to
the [JSON Lines format](https://jsonlines.org/).

### Features

- 🌎 Provides an API similar to Python's standard `json` module.
- 🚀 Supports custom serialization/deserialization callbacks, with the standard `json` module as the default.
- 🗜️ Supports compression and decompression using `gzip`, `bzip2`, and `xz` formats.
- 🔧 Can load files with broken lines, skipping any malformed entries.
- 📦 Includes an easy-to-use utility for incrementally writing to multiple JSON Lines files.

## Installation

To install **jsonl** using `pip`, run the following command:

```bash
pip install py-jsonl
```

## Getting Started

**Dumping Data to a JSON Lines File**

Use `jsonl.dump` to write an iterable of dictionaries to a JSON Lines file:

```python
import jsonl

data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, "file.jsonl")
```

**Loading Data from a JSON Lines File**

Use `jsonl.load` to load a JSON Lines file into an iterable of objects:

```python
import jsonl

iterable = jsonl.load("file.jsonl")
print(tuple(iterable))
```

**Incremental Writing to Multiple JSON Lines Files**

This example uses `jsonl.dump_fork` to incrementally write daily temperature data for multiple cities to separate JSON
Lines files, exporting records for the first days of specified years.
It efficiently manages data by creating individual files for each city, optimizing memory usage.

```python
import datetime
import itertools
import random

import jsonl


def get_temperature_by_city():
    """
    Generates files for each city with daily temperature data for the initial days of
    the specified years.
    """

    years = [2023, 2024]
    first_days = 10
    cities = ["New York", "Los Angeles", "Chicago"]

    for year, city in itertools.product(years, cities):
        start = datetime.datetime(year, 1, 1)
        dates = (start + datetime.timedelta(days=day) for day in range(first_days))
        daily_temperature = (
            {"date": date.isoformat(), "city": city, "temperature": round(random.uniform(-10, 35), 2)}
            for date in dates
        )
        yield (f"{city}.jsonl", daily_temperature)

# Write the generated data to files in JSON Lines format
jsonl.dump_fork(get_temperature_by_city())
```

## Documentation

For more detailed information and usage examples, refer to the
project [documentation](https://rmoralespp.github.io/jsonl/)

## Development

To contribute to the project, you can run the following commands for testing and documentation:

### Running Unit Tests

Install the development dependencies and run the tests:

```
(env)$ pip install -r requirements-dev.txt  # Skip if already installed
(env)$ pytest tests/
(env)$ pytest --cov jsonl # Run tests with coverage
```

### Building the Documentation

To build the documentation locally, use the following commands:

```
(env)$ pip install -r requirements-docs.txt   # Skip if already installed
(env)$ mkdocs serve # Start live-reloading docs server
(env)$ mkdocs build # Build the documentation site
```

## License

This project is licensed under the [MIT license](LICENSE).
