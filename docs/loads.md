# jsonl.loads

Deserialize a JSON Lines formatted string into an object iterator.

## Function Signature

```python
jsonl.loads(
    text,
    *,
    broken=False,
    cls=None,
    **kwargs,
)
```

### Parameters

| Parameter  | Type                                          | Default            | Description                                                |
|------------|-----------------------------------------------|--------------------|------------------------------------------------------------|
| `text`     | `str`                                         | *(required)*       | JSON Lines formatted string                                |
| `broken`   | `bool`                                        | `False`            | If true, skip broken lines (only logging a warning)        |
| `cls`      | `type[json.JSONDecoder]` `Callable` or `None` | `json.JSONDecoder` | Custom decoder                                             |
| `**kwargs` |                                               |                    | Additional keyword arguments passed to the `cls` decoder   |

### Returns

`Iterator[Any]` — An iterator yielding one deserialized object per line.

---

## Examples

### Basic usage

```python
import jsonl

text = '{"foo": 1}\n{"bar": 2}\n'
for item in jsonl.loads(text):
    print(item)
```

*Output:*

```text
{'foo': 1}
{'bar': 2}
```

### Roundtrip with dumps

```python
import jsonl

data = [{"name": "Alice"}, {"name": "Bob"}]
text = jsonl.dumps(data)

for item in jsonl.loads(text):
    print(item)
```

*Output:*

```text
{'name': 'Alice'}
{'name': 'Bob'}
```

### Tolerant parsing

```python
import jsonl

text = '{"a": 1}\nnot json\n{"b": 2}\n'
result = list(jsonl.loads(text, broken=True))
print(result)
```

*Output:*

```text
[{'a': 1}, {'b': 2}]
```
