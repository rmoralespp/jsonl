import operator
import shutil

import pytest

import jsonl
import tests


@pytest.mark.parametrize("pattern, match_members", [
    ("file3", []),
    ("file1", ["file1"]),
    ("file*", ["file1", "file2"]),
])
@pytest.mark.parametrize("archive_format", ["tar", "zip"])
def test_load_archive(pattern, match_members, tmp_dir, archive_format, file_extension):
    pattern += file_extension
    if archive_format == "tar":
        pattern = "./" + pattern  # tar requires a leading slash for patterns
        match_members = [f"./{member}" for member in match_members]

    members = [f"file1{file_extension}", f"file2{file_extension}"]
    match_members = [member + file_extension for member in match_members]

    root_dir = tmp_dir / "archive"
    root_dir.mkdir(parents=True, exist_ok=True)
    for member in members:
        with jsonl._xopen(root_dir / member, mode="wb") as fp:  # write into a binary file
            content = tests.string_data.encode(jsonl._utf_8)
            fp.write(content)

    archivepath = str(root_dir / "myarchive")
    archivepath = shutil.make_archive(archivepath, archive_format, root_dir=root_dir, base_dir=".")

    order_by = operator.itemgetter(0)
    expected = sorted(((name, tests.data) for name in match_members), key=order_by)
    result = jsonl.load_archive(archivepath, pattern=pattern)
    result = sorted(((name, list(data)) for name, data in result), key=order_by)
    assert result == expected


def test_unsupported_archive_format(tmp_dir):
    unsupported_file = tmp_dir / "unsupported.rar"
    unsupported_file.write_bytes(b"Not a valid archive")
    with pytest.raises(ValueError, match="Unsupported archive format"):
        next(jsonl.load_archive(unsupported_file))
