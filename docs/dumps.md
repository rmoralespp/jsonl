# jsonl.dumps

Serialize an iterable of objects into a JSON Lines formatted string.

## Function Signature

```python
jsonl.dumps(
    iterable,
    *,
    cls=None,
    **kwargs,
)
```

### Parameters

| Parameter  | Type                                          | Default            | Description                                               |
|------------|-----------------------------------------------|--------------------|-----------------------------------------------------------|
| `iterable` | `Iterable[Any]`                               | *(required)*       | Iterable of objects to serialize                          |
| `cls`      | `type[json.JSONEncoder]` `Callable` or `None` | `json.JSONEncoder` | Custom encoder                                            |
| `**kwargs` |                                               |                    | Additional keyword arguments passed to the `cls`  encoder |

### Returns

`str` — A string with one JSON object per line.

---

## Examples

### Basic usage

```python
import jsonl

data = [{"foo": 1}, {"bar": 2}]
result = jsonl.dumps(data)
print(result)
```

*Output:*

```text
{"foo": 1}
{"bar": 2}
```

### With custom serialization

```python
import jsonl

data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]

# Compact output
result = jsonl.dumps(data, separators=(",", ":"))
print(result)
```

*Output:*

```text
{"name":"Alice","age":30}
{"name":"Bob","age":25}
```

### With sorted keys

```python
import jsonl

data = [{"z": 1, "a": 2}, {"m": 3, "b": 4}]

result = jsonl.dumps(data, sort_keys=True)
print(result)
```

*Output:*

```text
{"a": 2, "z": 1}
{"b": 4, "m": 3}
```
