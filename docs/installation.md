# Installation

## Requirements

- **Python 3.8** or higher
- No external dependencies — **jsonl** uses only the Python standard library

## Install via pip

```bash
pip install py-jsonl
```

To upgrade to the latest version:

```bash
pip install py-jsonl --upgrade
```

## Optional: High-Performance JSON Libraries

**jsonl** works with the standard `json` module out of the box. For better performance, you can use
alternative JSON libraries by passing them via the `json_dumps` / `json_loads` parameters:

```bash
pip install orjson
```

```python
import orjson
import jsonl

data = [{"name": "Alice"}, {"name": "Bob"}]

# Write using orjson (returns bytes, use text_mode=False)
jsonl.dump(data, "file.jsonl", json_dumps=orjson.dumps, text_mode=False)

# Read using orjson
for item in jsonl.load("file.jsonl", json_loads=orjson.loads):
    print(item)
```