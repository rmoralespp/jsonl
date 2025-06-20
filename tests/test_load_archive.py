import pathlib
import shutil
import tempfile

import pytest

import jsonl
import tests


@pytest.fixture()
def tmp_dir():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield pathlib.Path(tmp_dir)


@pytest.mark.parametrize("pattern, match_members", [
    ("*", 2),
    ("file1", 1),
    ("file3", 0),
    ("file*", 2),
    ("file?", 2),
    ("file[12]", 2),
    ("file[!3]", 2),
    ("file[1-2]", 2),
])
@pytest.mark.parametrize("format", ["tar", "zip"])
def test_load_archive(pattern, match_members, tmp_dir, format, file_extension):
    pattern += file_extension
    if format == "tar":
        pattern = "./" + pattern  # tar requires a leading slash for patterns

    members = [f"file1{file_extension}", f"file2{file_extension}"]
    root_dir = tmp_dir / "archive"
    root_dir.mkdir(parents=True, exist_ok=True)
    for member in members:
        # Prepare a file with JSON lines
        with jsonl.xopen(root_dir / member, mode="wb") as fp:  # write into a binary file
            content = tests.string_data.encode(jsonl.utf_8)
            fp.write(content)

    archivepath = str(root_dir / "myarchive")
    archivepath = shutil.make_archive(archivepath, format, root_dir=root_dir, base_dir=".")

    expected = tests.data * match_members
    result = list(jsonl.load_archive(archivepath, pattern=pattern))
    assert result == expected


def test_unsupported_archive_format(tmp_dir):
    unsupported_file = tmp_dir / "unsupported.rar"
    unsupported_file.write_bytes(b"Not a valid archive")
    with pytest.raises(ValueError, match="Unsupported archive format"):
        next(jsonl.load_archive(unsupported_file))
