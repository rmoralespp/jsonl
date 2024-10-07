# Dump to multiple jsonlines files

Dump multiple iterables to the specified jsonlines file paths, optimizing memory usage.

The files can be compressed using `gzip`, `bzip2`, or `xz` formats. If the file extension is not recognized, it will be
dumped to a text file.

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
