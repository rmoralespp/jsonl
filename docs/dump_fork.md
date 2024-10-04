##### Dump fork (Incremental dump)

Incrementally dumps multiple iterables into the specified jsonlines file paths,
effectively reducing memory consumption.

**Examples:**

`pip install orjson ujson`  # Ignore this command if these libraries are already installed.

```python
import orjson
import ujson
import jsonl


def worker():
    yield ("num.jsonl", ({"value": 1}, {"value": 2}))
    yield ("foo.jsonl", iter(({"a": "1"}, {"b": 2})))
    yield ("num.jsonl", [{"value": 3}])
    yield ("foo.jsonl", ())


jsonl.dump_fork(worker())  # using (json)
jsonl.dump_fork(worker(), json_dumps=ujson.dumps, ensure_ascii=False)  # using (ujson)
jsonl.dump_fork(worker(), json_dumps=orjson.dumps)  # using (orjson)
```
