import os.path

import pytest

import jsonl


def _get_loaded_data(path):
    loaded = ((name.lstrip("./") if "tar" in path else name, list(data)) for name, data in jsonl.load_archive(path))
    return sorted(loaded, key=lambda x: x[0])


def test_dump_archive(tmp_dir, archive_extension):
    path = str(tmp_dir / f"archive{archive_extension}")
    data = [
        ("file1.jsonl", [{"key": "value1"}, {"key": "value2"}]),
        ("path/to/file2.jsonl", [{"key": "value3"}]),
        ("path/to/file3.jsonl", []),
        ("path/to/file2.jsonl", [{"key": "value4"}]),
    ]
    # Execute the function to dump the archive
    result = jsonl.dump_archive(path, data)
    # Load the archive to verify its contents
    loaded = _get_loaded_data(result)
    expected_data = [
        ('file1.jsonl', [{'key': 'value1'}, {'key': 'value2'}]),
        ('path/to/file2.jsonl', [{'key': 'value3'}, {'key': 'value4'}]),
        ('path/to/file3.jsonl', []),
    ]
    # Verify the path and loaded data
    assert result == path
    assert loaded == expected_data


def test_invalid_extension():
    path = "archive.invalid"
    data = [("file.jsonl", [{"key": "value"}])]
    with pytest.raises(ValueError, match=f"Unsupported archive extension: {path}"):
        jsonl.dump_archive(path, data)


def test_invalid_filepath(tmp_dir):
    arc_path = "archive.zip"
    filepath = os.path.join(tmp_dir, "file.jsonl")
    data = [filepath, [{"key": "value"}]]
    with pytest.raises(ValueError):
        jsonl.dump_archive(arc_path, data)


@pytest.mark.parametrize("dump_if_empty", [True, False])
def test_empty_data(tmp_dir, dump_if_empty):
    path = str(tmp_dir / "empty_archive.zip")
    data = [("file1.jsonl", []), ]
    # Execute the function to dump the archive
    result = jsonl.dump_archive(path, data, dump_if_empty=dump_if_empty)
    # Verify the path and loaded data
    if dump_if_empty:
        # Load the archive to verify its contents
        loaded = _get_loaded_data(result)
        assert result == path
        assert loaded == data  # Expecting an empty archive
    else:
        # If not dumping empty, the result should be the same as the input path
        assert result is None
        # Verify that no archive was created
        assert not os.path.exists(path)
