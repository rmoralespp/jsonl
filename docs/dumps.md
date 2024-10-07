##### Serialize an iterable into a JSON Lines formatted string.

```python
import jsonl

data = ({'foo': 1}, {'bar': 2})
result = jsonl.dumps(data)
print(result)
```
