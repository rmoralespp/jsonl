# jsonl.loader

Low-level generator that deserializes a line stream into Python objects.
This is the building block used internally by `jsonl.load`.

## Function Signature

```python
jsonl.loader(stream, broken, *, cls=None, **kwargs)
```

### Parameters

| Parameter  | Type                                             | Default            | Description                                                       |
|------------|--------------------------------------------------|--------------------|-------------------------------------------------------------------|
| `stream`   | iterable of `str` or `bytes`                     | *(required)*       | Any iterable yielding one JSON line per iteration                 |
| `broken`   | `bool`                                           | *(required)*       | If `True`, skip malformed lines and log a warning                 |
| `cls`      | `type[json.JSONDecoder]` or `Callable` or `None` | `json.JSONDecoder` | Custom decoder                                                    |
| `**kwargs` |                                                  |                    | Keyword arguments passed to the Custom decoder (`cls`)            |

### Returns

`Iterator[Any]` — An iterator yielding deserialized Python objects, one per line.

---

## Examples

### Deserialize from an in-memory list

```python
import jsonl

lines = ['{"name": "Alice"}\n', '{"name": "Bob"}\n']

for item in jsonl.loader(lines, False):
    print(item)
```

*Output:*

```text
{'name': 'Alice'}
{'name': 'Bob'}
```

### Deserialize bytes lines

```python
import jsonl

lines = [b'{"x": 1}\n', b'{"x": 2}\n']

for item in jsonl.loader(lines, False):
    print(item)
```

### Skip malformed lines

```python
import jsonl

lines = ['{"valid": true}\n', 'not json\n', '{"also": "valid"}\n']

for item in jsonl.loader(lines, True):
    print(item)
```

*Output:*

```text
{'valid': True}
{'also': 'valid'}
```

### With a custom decoder

```python
import orjson
import jsonl

lines = [b'{"name": "Alice"}\n', b'{"name": "Bob"}\n']

for item in jsonl.loader(lines, False, cls=orjson.loads):
    print(item)
```
