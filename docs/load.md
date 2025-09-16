# Load JSON Lines files 

Load JSON Lines **(jsonl)** files incrementally, supporting both uncompressed and compressed formats, handling broken
lines, and allowing custom deserialization and opener callbacks.

It also allows loading from URLs and `urllib` requests.

<a id="note-compression"></a>
!!! note
    Supported compression formats are: **gzip (.gz), bzip2 (.bz2), xz (.xz)**
    
    If a file extension is not provided or is not recognized, the compression format will be automatically detected by reading the file's **"magic number."**
    
    If the detection fails, the file is considered uncompressed.
```

#### Load an uncompressed file given a path.

```python
import jsonl

path = "file.jsonl"

# Example data to save in the file
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Save the data to the jsonl file
jsonl.dump(data, path)

# Load the file as an iterator
iterator = jsonl.load(path)
print(tuple(iterator))
```

#### Load a compressed file given a path.

Check [note](#note-compression) for more details

```python
import jsonl

path = "file.jsonl.gz" # gzip compressed file, but it can be ".bz2" or ".xz"

# Example data to save in the file
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Save the data to the compressed jsonl file
jsonl.dump(data, path)

# Load the compressed file as an iterator
iterator = jsonl.load(path)
print(tuple(iterator))
```

#### Load a file from an open file object.

!!! tip
    This is useful when you need to load a file from a custom source.

```python
import jsonl

path = "file.jsonl"

# Example data to save in the file
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Save the data to the compressed jsonl file
jsonl.dump(data, path)

# Load the file using an open file object
with open(path) as fp:
    iterator = jsonl.load(fp)
    print(tuple(iterator))
```

#### Load from a URL.

You can load a JSON Lines directly from a URL incrementally, if needed you can also create custom 
requests using `urllib.request.Request`.

```python
import urllib.request
import jsonl

# Load data from a URL
iterator = jsonl.load("https://example.com/file.jsonl")
print(tuple(iterator))

# Load data from a urllib request to handle custom requests
req = urllib.request.Request("https://example.com/file.jsonl", headers={"Accept": "application/jsonl"})
iterator = jsonl.load(req)
print(tuple(iterator))
```

#### Load a file containing broken lines.

!!! warning
    If the **broken** parameter is set to `False`, the function will raise an `Exception` when it encounters a broken line.
    If set to `True`, the function will skip the broken line, continue reading the file, and log a warning message.

```python
import jsonl

# Create a file with broken JSON lines
with open("file.jsonl", mode="wt", encoding="utf-8") as fp:
    fp.write('{"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]}\n')
    fp.write('{"name": "May", "wins": []\n')  # missing closing bracket
    fp.write('{"name": "Richard", "wins": []}\n')

# Load the jsonl file, skipping broken lines
iterator = jsonl.load("file.jsonl", broken=True)
print(tuple(iterator))
```

*Output:*

```console
WARNING:root:Broken line at 2: Expecting ',' delimiter: line 2 column 1 (char 28)
({'name': 'Gilbert', 'wins': [['straight', '7♣'], ['one pair', '10♥']]}, {'name': 'Richard', 'wins': []})
```

#### Load a file using a custom deserialization.

The `json_loads` parameter allows for custom deserialization and must take a JSON-formatted
string as input and return a Python object.

!!! tip
    Commonly, libraries like `orjson` or `ujson` are used for faster performance, or you can implement your own
    custom deserialization function for specific needs.

The following example demonstrates how to use the `json_loads` parameter to deserialize the data
using the `orjson` and `ujson` libraries. Make sure to install these libraries to run the example.

```console
pip install orjson ujson # Ignore this command if these libraries are already installed.
```

Now, you can use these libraries to load the JSON lines:

```python
import orjson
import ujson

import jsonl

path = "file.jsonl"

# Example data to save in the file
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Save the data to the jsonl file
jsonl.dump(data, path)

# Load the file using ujson
iterator1 = jsonl.load(path, json_loads=ujson.loads)

# Load the file using orjson
iterator2 = jsonl.load(path, json_loads=orjson.loads)

print(tuple(iterator1))
print(tuple(iterator2))
```

#### Load a file using a custom opener.

The `opener` parameter allows loading files from custom sources, such as a ZIP archive. Here’s how to use it:

```python
import zipfile

import jsonl

# Create a ZIP file containing a jsonlines file
zip_path = "data.zip"
jsonl_path = "file.jsonl"
data = [
    {"name": "Gilbert", "wins": [["straight", "7♣"], ["one pair", "10♥"]]},
    {"name": "May", "wins": []},
]

# Save the data to the jsonl file
jsonl.dump(data, jsonl_path)

# Create a ZIP file and add the jsonl file to it
with zipfile.ZipFile(zip_path, 'w') as zf:
    zf.write(jsonl_path)


# Define a custom opener function to read from the ZIP file
def opener(name, *args, **kwargs):
    return zipfile.ZipFile(name).open(jsonl_path)


# Load the jsonl file from the ZIP archive using the opener
iterator = jsonl.load(zip_path, opener=opener)
print(tuple(iterator))
```
