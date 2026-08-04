# jsonl.dumper

Low-level generator that yields formatted JSON Lines strings (or bytes) from an iterable of objects.
This is the building block used internally by `jsonl.dump` and `jsonl.dumps`.

## Function Signature

```python
jsonl.dumper(iterable, *, text_mode=True, cls=None, **kwargs)
```

### Parameters

| Parameter   | Type                                          | Default            | Description                                               |
|-------------|-----------------------------------------------|--------------------|-----------------------------------------------------------|
| `iterable`  | `Iterable[Any]`                               | *(required)*       | Iterable of JSON-serializable objects                     |
| `text_mode` | `bool`                                        | `True`             | If `True`, yield `str` lines; if `False`, yield `bytes`   |
| `cls`       | `type[json.JSONEncoder]` `Callable` or `None` | `json.JSONEncoder` | Custom encoder                                            |
| `**kwargs`  |                                               |                    | Additional keyword arguments passed to the `cls` encoder  |

### Returns

`Iterator[str | bytes]` — A generator yielding one formatted line per object (including trailing newline).

---

## Examples

### Basic usage

```python
import jsonl

data = [{"name": "Alice"}, {"name": "Bob"}]

for line in jsonl.dumper(data):
    print(repr(line))
```

*Output:*

```text
'{"name": "Alice"}\n'
'{"name": "Bob"}\n'
```

### Yield bytes

```python
import jsonl

data = [{"x": 1}, {"x": 2}]

for line in jsonl.dumper(data, text_mode=False):
    print(repr(line))
```

*Output:*

```text
b'{"x": 1}\n'
b'{"x": 2}\n'
```

### Stream to a custom destination

```python
import jsonl

data = [{"event": "click"}, {"event": "scroll"}]

# Write lines to stdout or any writable target
import sys
for line in jsonl.dumper(data):
    sys.stdout.write(line)
```

### With orjson

```python
import orjson
import jsonl

data = [{"name": "Alice"}, {"name": "Bob"}]

for line in jsonl.dumper(data, text_mode=False, cls=orjson.dumps):
    print(repr(line))
```
