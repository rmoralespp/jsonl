# Dump to multiple jsonlines files

Dump multiple iterables incrementally to the specified jsonlines file paths, optimizing memory usage.

The files can be compressed using `gzip`, `bzip2`, or `xz` formats. If the file extension is not recognized, it will be
dumped to a text file.

**Example #1**

This example uses `jsonl.dump_fork` to incrementally write structured data to multiple **.jsonl** files—one per key (in this case, player name). 
This helps organize and efficiently store data for separate entities.
This example creates individual JSON Lines files for each player, storing their respective wins.


```python
# -*- coding: utf-8 -*-

import jsonl


def generate_win_data():
    """Yield player wins data for multiple players."""

    data = (
        {
            "name": "Gilbert",
            "wins": [
                {"hand": "straight", "card": "7♣"},
                {"hand": "one pair", "card": "10♥"},
            ]
        },
        {
            "name": "May",
            "wins": [
                {"hand": "two pair", "card": "9♠"},
            ]
        },
        {
            "name": "Gilbert",
            "wins": [
                {"hand": "three of a kind", "card": "A♦"},
            ]
        }
    )
    for player in data:
        name = player["name"]
        yield (f"{name}.jsonl", player["wins"])


# Write the generated data to files in JSON Lines format
jsonl.dump_fork(generate_win_data())
```

**Example #2**

This example demonstrates how to dump data using different JSON libraries.
You can install `orjson` and `ujson` to run the following example.

```bash
pip install orjson ujson # Ignore this command if these libraries are already installed.
```

```python
# -*- coding: utf-8 -*-

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
