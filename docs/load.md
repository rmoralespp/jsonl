##### load

Deserialize a UTF-8 encoded jsonlines file into an iterable of Python objects.

**Examples:**

Load an uncompressed file from the specified path.

```python
import jsonl

path = "file.jsonl"
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, path)
iterable = jsonl.load(path)
print(tuple(iterable))
```

Load a compressed file from the specified path.

```python
import jsonl

path = "file.jsonl.gz"
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, path)
iterable = jsonl.load(path)
print(tuple(iterable))
```

Load a compressed file from the specified open file object.

```python
import gzip
import jsonl

path = "file.jsonl.gz"
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, path)
with gzip.open(path, mode="rb") as fp:
    iterable = jsonl.load(fp)
    print(tuple(iterable))
```

Load a file containing broken lines, skipping any malformed lines.

```python
import jsonl

with open("file.jsonl", mode="wt", encoding="utf-8") as fp:
    fp.write('{"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]}\n')
    fp.write('{"name": "May", "wins": []\n')  # missing closing bracket
    fp.write('{"name": "Richard", "wins": []}\n')

iterable = jsonl.load("file.jsonl", broken=True)
print(tuple(iterable))
```

Load a file using a custom deserialization callback.

`pip install orjson ujson`  # Ignore this command if these libraries are already installed.

```python
import orjson
import ujson
import jsonl

path = "file.jsonl"
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

jsonl.dump(data, path)

iterable1 = jsonl.load(path, json_loads=ujson.loads)  # using (ujson)
iterable2 = jsonl.load(path, json_loads=orjson.loads)  # using (orjson)
print(tuple(iterable1))
print(tuple(iterable2))
```
