# jsonl.dump_fork

Write data to multiple JSON Lines files simultaneously. This is useful when you need to split data
across different files based on some criteria, while minimizing memory usage through incremental writing.

## Function Signature

```python
jsonl.dump_fork(
    paths,
    *,
    opener=None,
    text_mode=True,
    dump_if_empty=True,
    json_dumps=None,
    **json_dumps_kwargs,
)
```

### Parameters

| Parameter             | Type                                  | Default      | Description                                                       |
|-----------------------|---------------------------------------|--------------|-------------------------------------------------------------------|
| `paths`               | `Iterable[tuple[str, Iterable[Any]]]` | *(required)* | Iterable of `(filepath, items)` tuples                            |
| `opener`              | `Callable` or `None`                  | `None`       | Custom function to open the given file paths                      |
| `text_mode`           | `bool`                                | `True`       | If `False`, write bytes instead of text                           |
| `dump_if_empty`       | `bool`                                | `True`       | If `False`, don't create empty files                              |
| `json_dumps`          | `Callable` or `None`                  | `None`       | Custom serialization function. Defaults to `json.dumps`           |
| `**json_dumps_kwargs` |                                       |              | Additional keyword arguments passed to the serialization function |

### Behavior

- If the same filepath appears multiple times, subsequent data is **appended** to the file.
- Files can use compression extensions (`.gz`, `.bz2`, `.xz`) and will be compressed accordingly.
- When `dump_if_empty=False`, files with no data are not created.

---

## Examples

### Split data into separate files

```python
import jsonl


def generate_player_files():
    """Yield (filepath, records) tuples — one file per player."""

    data = [
        {"name": "Gilbert", "wins": [{"hand": "straight", "card": "7♣"}]},
        {"name": "May", "wins": [{"hand": "two pair", "card": "9♠"}]},
        {"name": "Gilbert", "wins": [{"hand": "three of a kind", "card": "A♦"}]},
    ]
    for player in data:
        yield (f"{player['name']}.jsonl", player["wins"])


jsonl.dump_fork(generate_player_files())
# Creates: Gilbert.jsonl (with 2 entries), May.jsonl (with 1 entry)
```

### Write to multiple files with static data

```python
import jsonl

data = [
    ("users.jsonl", [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]),
    ("orders.jsonl", [{"id": 1, "total": 99.90}, {"id": 2, "total": 45.00}]),
    ("users.jsonl", [{"name": "Eve", "age": 28}]),  # Appends to users.jsonl
]

jsonl.dump_fork(data)
```

### Custom serialization

```python
import orjson
import jsonl


def worker():
    yield ("numbers.jsonl", ({"value": 1}, {"value": 2}))
    yield ("strings.jsonl", iter(({"a": "1"}, {"b": "2"})))
    yield ("numbers.jsonl", [{"value": 3}])


# Using orjson for faster serialization
jsonl.dump_fork(worker(), json_dumps=orjson.dumps, text_mode=False)
```
