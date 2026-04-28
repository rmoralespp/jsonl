# -*- coding: utf-8 -*-

import io
import operator
import os
import shutil
import tarfile

import pytest

import jsonl
import tests


@pytest.mark.parametrize("pattern, match_members", [
    ("file3", []),
    ("file1", ["file1"]),
    ("file*", ["file1", "file2"]),
])
@pytest.mark.parametrize("with_unknown_ext", [True, False])
@pytest.mark.parametrize("archive_format", ["tar", "zip"])
def test_load_archive(pattern, match_members, tmp_dir, archive_format, file_extension, with_unknown_ext):
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

    if with_unknown_ext:
        # Rename files to have an unknown extension after writing valid data
        for member in members:
            new_member = member + ".unknown"
            os.rename(root_dir / member, root_dir / new_member)
        # Adjust pattern to match the new extension
        pattern += ".unknown"

    archivepath = str(root_dir / "myarchive")
    archivepath = shutil.make_archive(archivepath, archive_format, root_dir=root_dir, base_dir=".")

    order_by = operator.itemgetter(0)
    expected = sorted(((name, tests.data) for name in match_members), key=order_by)
    result = jsonl.load_archive(archivepath, pattern=pattern)
    result = sorted(((name, list(data)) for name, data in result), key=order_by)
    if with_unknown_ext:
        # Adjust expected names to have the .unknown extension
        expected = [(name + ".unknown", data) for name, data in expected]
    assert result == expected


def test_unsupported_archive_format(tmp_dir):
    unsupported_file = tmp_dir / "unsupported.rar"
    unsupported_file.write_bytes(b"Not a valid archive")
    with pytest.raises(ValueError, match="Unsupported archive format"):
        next(jsonl.load_archive(unsupported_file))


def test_url_using_opener():
    with pytest.raises(ValueError):
        next(jsonl.load_archive("http://foo.com", opener=object()))


@pytest.mark.parametrize("filename", ("archive.zip", "archive.tar"))
def test_http_server_uri_url(http_server, filename):
    url = http_server + "/" + filename
    loaded = jsonl.load_archive(url)
    loaded = [(name, list(data)) for name, data in loaded]
    expected = [('foo.jsonl', tests.data), ('var.jsonl', tests.data)]
    assert loaded == expected


def test_load_archive_from_bytesio_tar():
    content = tests.string_data.encode(jsonl._utf_8)
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w") as tar:
        info = tarfile.TarInfo(name="file1.jsonl")
        info.size = len(content)
        tar.addfile(info, io.BytesIO(content))
    buf.seek(0)

    expected = [("file1.jsonl", tests.data)]
    result = [(name, list(data)) for name, data in jsonl.load_archive(buf, pattern="*.jsonl")]
    assert result == expected


def test_load_archive_tar_skips_directory_members(tmp_dir):
    content = tests.string_data.encode(jsonl._utf_8)
    archive_path = str(tmp_dir / "test.tar")
    with tarfile.open(archive_path, "w") as tar:
        dir_info = tarfile.TarInfo(name="subdir.jsonl")
        dir_info.type = tarfile.DIRTYPE
        tar.addfile(dir_info)

        file_info = tarfile.TarInfo(name="file1.jsonl")
        file_info.size = len(content)
        tar.addfile(file_info, io.BytesIO(content))

    expected = [("file1.jsonl", tests.data)]
    result = [(name, list(data)) for name, data in jsonl.load_archive(archive_path, pattern="*.jsonl")]
    assert result == expected
