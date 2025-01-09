# Dump to multiple jsonlines files

Dump multiple iterables incrementally to the specified jsonlines file paths, optimizing memory usage.

The files can be compressed using `gzip`, `bzip2`, or `xz` formats. If the file extension is not recognized, it will be
dumped to a text file.

**Example #1**

This example uses `jsonl.dump_fork` to incrementally write fake daily temperature data for multiple cities to separate JSON
Lines files, exporting records for the first days of specified years.
It efficiently manages data by creating individual files for each city, optimizing memory usage.

```python
import datetime
import itertools
import random

import jsonl


def fetch_temperature_by_city():
    """
    Yielding filenames for each city with fake daily temperature data for the initial days of
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
jsonl.dump_fork(fetch_temperature_by_city())
```

**Example #2**

This example demonstrates how to dump data using different JSON libraries.
You can install `orjson` and `ujson` to run the following example.

```console
pip install orjson ujson # Ignore this command if these libraries are already installed.
```

```python
import orjson
import ujson
import jsonl


def worker():
    yield ("num.jsonl", ({"value": 1}, {"value": 2}))
    yield ("foo.jsonl", iter(({"a": "1"}, {"b": 2})))
    yield ("num.jsonl", [{"value": 3}])
    yield ("foo.jsonl", ())


# Dump the data using the default json.dumps function.
jsonl.dump_fork(worker())

# Dump the data using the ujson library.
jsonl.dump_fork(worker(), json_dumps=ujson.dumps, ensure_ascii=False)

# Dump the data using the orjson library.
jsonl.dump_fork(worker(), json_dumps=orjson.dumps)  # using (orjson)
```
