# -*- coding: utf-8 -*-

import contextlib
import errno
import gzip
import importlib.metadata
import io
import logging
import os
import stat
import subprocess
import sys
import types
import zipfile

import pytest

import jsonl
import tests

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "data"))


class ChunkedBytesIO(io.BytesIO):
    """Expose at most one byte per read to simulate a fragmented pipe."""

    def read(self, size=-1):
        return super().read(1 if size < 0 else min(size, 1))

    read1 = read


class FlushErrorStream(io.StringIO):
    """Capture writes but fail when the CLI performs its final flush."""

    def __init__(self, error):
        super().__init__()
        self.error = error

    def flush(self):
        raise self.error


def set_stdin(monkeypatch, data, *, peekable=False):
    """Replace `sys.stdin` with a fake exposing a binary `buffer`."""

    if isinstance(data, str):
        data = data.encode("utf-8")
    buffer = io.BufferedReader(io.BytesIO(data)) if peekable else io.BytesIO(data)
    monkeypatch.setattr("sys.stdin", types.SimpleNamespace(buffer=buffer))


def test_stdin_to_stdout_roundtrip(monkeypatch, capsys):
    set_stdin(monkeypatch, "[1]\n[2]\n[3]\n")
    assert jsonl.main([]) == 0
    assert capsys.readouterr().out == "[1]\n[2]\n[3]\n"


def test_dash_infile_reads_stdin(monkeypatch, capsys):
    set_stdin(monkeypatch, "[1]\n")
    assert jsonl.main(["-"]) == 0
    assert capsys.readouterr().out == "[1]\n"


def test_empty_stdin(monkeypatch, capsys):
    set_stdin(monkeypatch, "")

    assert jsonl.main([]) == 0
    assert not capsys.readouterr().out


def test_compact(monkeypatch, capsys):
    set_stdin(monkeypatch, '{"b": 2, "a": 1}\n')
    assert jsonl.main(["--compact"]) == 0
    assert capsys.readouterr().out == '{"b":2,"a":1}\n'


def test_sort_keys(monkeypatch, capsys):
    set_stdin(monkeypatch, '{"b": 2, "a": 1}\n')
    assert jsonl.main(["--sort-keys"]) == 0
    assert capsys.readouterr().out == '{"a": 1, "b": 2}\n'


def test_default_emits_utf8(monkeypatch, capsys):
    set_stdin(monkeypatch, '{"x": "\\u00f1"}\n')
    assert jsonl.main([]) == 0
    assert capsys.readouterr().out == '{"x": "\u00f1"}\n'


def test_ascii_flag_escapes(monkeypatch, capsys):
    set_stdin(monkeypatch, '{"x": "\\u00f1"}\n')
    assert jsonl.main(["--ascii"]) == 0
    assert capsys.readouterr().out == '{"x": "\\u00f1"}\n'


def test_file_to_file(tmp_dir):
    src = tmp_dir / "in.jsonl"
    dst = tmp_dir / "out.jsonl"
    tests.write_text(str(src), "[1]\n[2]\n")
    assert jsonl.main([str(src), str(dst)]) == 0
    assert list(jsonl.load(str(dst))) == [[1], [2]]


@pytest.mark.parametrize("extension", sorted(jsonl.extensions))
def test_output_compression(tmp_dir, extension):
    src = tmp_dir / "in.jsonl"
    dst = tmp_dir / ("out.jsonl" + extension)
    tests.write_text(str(src), "[1]\n[2]\n")
    assert jsonl.main([str(src), str(dst)]) == 0
    assert list(jsonl.load(str(dst))) == [[1], [2]]


def test_zstd_output_rejected_when_unavailable(tmp_dir, capsys, monkeypatch):
    src = tmp_dir / "in.jsonl"
    dst = tmp_dir / "out.jsonl.zst"
    tests.write_text(str(src), "[1]\n")
    monkeypatch.setattr(jsonl, "zstd", None)

    assert jsonl.main([str(src), str(dst)]) == 3
    assert not dst.exists()
    assert "Zstandard compression is unavailable" in capsys.readouterr().err


def test_zstd_input_rejected_when_unavailable(monkeypatch, capsys):
    set_stdin(monkeypatch, b"\x28\xb5\x2f\xfdinvalid", peekable=True)
    monkeypatch.setattr(jsonl, "zstd", None)

    assert jsonl.main([]) == 3
    assert "Zstandard compression is unavailable" in capsys.readouterr().err


def test_input_compression_stdin(monkeypatch, capsys):
    set_stdin(monkeypatch, gzip.compress(b"[1]\n[2]\n"))
    assert jsonl.main([]) == 0
    assert capsys.readouterr().out == "[1]\n[2]\n"


def test_input_compression_fragmented_stdin(monkeypatch, capsys):
    stream = ChunkedBytesIO(gzip.compress(b"[1]\n[2]\n"))
    monkeypatch.setattr("sys.stdin", types.SimpleNamespace(buffer=stream))

    assert jsonl.main([]) == 0
    assert capsys.readouterr().out == "[1]\n[2]\n"


def test_broken_false_aborts(monkeypatch, capsys):
    set_stdin(monkeypatch, "[1]\nNOPE\n[2]\n")
    assert jsonl.main([]) == 1
    captured = capsys.readouterr()
    assert captured.out == "[1]\n"  # streamed before the error
    assert "Broken line at 2" in captured.err


def test_broken_true_skips(monkeypatch, capsys):
    set_stdin(monkeypatch, "[1]\nNOPE\n[2]\n")
    assert jsonl.main(["--broken"]) == 1
    captured = capsys.readouterr()
    assert captured.out == "[1]\n[2]\n"
    assert "Broken line at 2" in captured.err


def test_broken_true_all_valid(monkeypatch, capsys):
    set_stdin(monkeypatch, "[1]\n[2]\n")
    assert jsonl.main(["--broken"]) == 0
    assert capsys.readouterr().out == "[1]\n[2]\n"


def test_broken_exit_code_independent_of_logging(monkeypatch, capsys):
    set_stdin(monkeypatch, "[1]\nNOPE\n[2]\n")
    logging.disable(logging.CRITICAL)
    try:
        assert jsonl.main(["--broken"]) == 1
    finally:
        logging.disable(logging.NOTSET)

    captured = capsys.readouterr()
    assert captured.out == "[1]\n[2]\n"
    assert "Broken line at 2" in captured.err


def test_broken_exit_code_independent_of_logger_disabled(monkeypatch, capsys):
    set_stdin(monkeypatch, "[1]\nNOPE\n[2]\n")
    monkeypatch.setattr(jsonl._logger, "disabled", True)

    assert jsonl.main(["--broken"]) == 1
    assert "Broken line at 2" in capsys.readouterr().err


def test_same_file_rejected(tmp_dir):
    src = tmp_dir / "in.jsonl"
    tests.write_text(str(src), "[1]\n")
    with pytest.raises(SystemExit) as exc:
        jsonl.main([str(src), str(src)])
    assert exc.value.code == 2


def test_same_file_hardlink_rejected(tmp_dir):
    src = tmp_dir / "in.jsonl"
    link = tmp_dir / "link.jsonl"
    tests.write_text(str(src), "[1]\n")
    try:
        os.link(str(src), str(link))  # hardlink: same inode, different path
    except (OSError, NotImplementedError, AttributeError):
        pytest.skip("hardlinks are not supported on this platform/filesystem")
    with pytest.raises(SystemExit) as exc:
        jsonl.main([str(src), str(link)])
    assert exc.value.code == 2


def test_output_preserved_on_error(tmp_dir):
    src = tmp_dir / "bad.jsonl"
    dst = tmp_dir / "dest.jsonl"
    tests.write_text(str(src), "[1]\nNOPE\n[2]\n")
    tests.write_text(str(dst), "OLD\n")
    assert jsonl.main([str(src), str(dst)]) == 1
    assert tests.read_text(str(dst)) == "OLD\n"
    leftovers = [p for p in os.listdir(tmp_dir) if p.startswith(".jsonl-tmp-")]
    assert leftovers == []


def test_broken_true_atomic_replace(tmp_dir):
    src = tmp_dir / "bad.jsonl"
    dst = tmp_dir / "dest.jsonl"
    tests.write_text(str(src), "[1]\nNOPE\n[2]\n")
    tests.write_text(str(dst), "OLD\n")
    assert jsonl.main(["--broken", str(src), str(dst)]) == 1
    assert list(jsonl.load(str(dst))) == [[1], [2]]


@pytest.mark.skipif(os.name == "nt", reason="POSIX file modes are not supported on Windows")
def test_atomic_replace_preserves_existing_mode(tmp_dir):
    src = tmp_dir / "in.jsonl"
    dst = tmp_dir / "out.jsonl"
    tests.write_text(str(src), "[1]\n")
    tests.write_text(str(dst), "OLD\n")
    os.chmod(dst, 0o640)

    assert jsonl.main([str(src), str(dst)]) == 0
    assert stat.S_IMODE(os.stat(dst).st_mode) == 0o640


@pytest.mark.skipif(os.name == "nt", reason="POSIX umask is not supported on Windows")
def test_atomic_new_output_respects_umask(tmp_dir):
    src = tmp_dir / "in.jsonl"
    dst = tmp_dir / "out.jsonl"
    tests.write_text(str(src), "[1]\n")
    previous_umask = os.umask(0o027)
    try:
        assert jsonl.main([str(src), str(dst)]) == 0
    finally:
        os.umask(previous_umask)

    assert stat.S_IMODE(os.stat(dst).st_mode) == 0o640


def test_member_archive(capsys):
    archive = os.path.join(DATA_DIR, "archive.zip")
    assert jsonl.main(["--member", "foo.jsonl", archive]) == 0
    assert capsys.readouterr().out.count("\n") == 4  # foo.jsonl has 4 records


def test_archive_auto_discovered(capsys):
    # A zip/tar path without --member auto-discovers its *.jsonl members.
    archive = os.path.join(DATA_DIR, "archive.zip")
    assert jsonl.main([archive]) == 0
    # archive.zip bundles foo.jsonl and var.jsonl (4 records each).
    assert capsys.readouterr().out.count("\n") == 8


def test_member_without_matches_preserves_output(tmp_dir, capsys):
    archive = tmp_dir / "data.zip"
    dst = tmp_dir / "out.jsonl"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("data.jsonl", "[1]\n")
    tests.write_text(str(dst), "OLD\n")

    assert jsonl.main(["--member", "missing-*.jsonl", str(archive), str(dst)]) == 3
    assert tests.read_text(str(dst)) == "OLD\n"
    assert "no archive members matched" in capsys.readouterr().err


def test_archive_auto_discovery_without_jsonl_preserves_output(tmp_dir, capsys):
    archive = tmp_dir / "data.zip"
    dst = tmp_dir / "out.jsonl"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("readme.txt", "not JSON Lines")
    tests.write_text(str(dst), "OLD\n")

    assert jsonl.main([str(archive), str(dst)]) == 3
    assert tests.read_text(str(dst)) == "OLD\n"
    assert "no archive members matched" in capsys.readouterr().err


def test_member_requires_file(monkeypatch):
    set_stdin(monkeypatch, "[1]\n")
    with pytest.raises(SystemExit) as exc:
        jsonl.main(["--member", "*.jsonl"])
    assert exc.value.code == 2


def test_member_broken(tmp_dir, capsys):
    archive = tmp_dir / "broken.zip"
    with zipfile.ZipFile(archive, "w") as zf:
        zf.writestr("a.jsonl", "[1]\nNOPE\n[2]\n")
    assert jsonl.main(["--broken", "--member", "*.jsonl", str(archive)]) == 1
    captured = capsys.readouterr()
    assert captured.out == "[1]\n[2]\n"
    assert "Broken line" in captured.err


def test_url_input(http_server, capsys):
    assert jsonl.main([http_server + "foo.jsonl"]) == 0
    assert capsys.readouterr().out.count("\n") == 4


def test_compressed_url_input(monkeypatch, capsys):
    response = io.BytesIO(gzip.compress(b"[1]\n[2]\n"))
    response.headers = types.SimpleNamespace(get_content_charset=lambda failobj: failobj)
    monkeypatch.setattr(
        jsonl.urllib.request,
        "urlopen",
        lambda _url: contextlib.nullcontext(response),
    )

    assert jsonl.main(["https://example.com/download?id=123"]) == 0
    assert capsys.readouterr().out == "[1]\n[2]\n"


def test_unexpected_error_exit_code(tmp_dir, capsys):
    missing = tmp_dir / "does-not-exist.jsonl"
    assert jsonl.main([str(missing)]) == 3
    assert "error" in capsys.readouterr().err


def test_archive_probe_errors_treated_as_plain_file(tmp_dir, monkeypatch, capsys):
    src = tmp_dir / "data.jsonl"
    tests.write_text(str(src), "[1]\n")

    def raise_oserror(_path):
        raise OSError

    def raise_tar_error(_path):
        raise jsonl.tarfile.TarError

    monkeypatch.setattr(jsonl.zipfile, "is_zipfile", raise_oserror)
    monkeypatch.setattr(jsonl.tarfile, "is_tarfile", raise_tar_error)

    assert jsonl.main([str(src)]) == 0
    assert capsys.readouterr().out == "[1]\n"


def test_version():
    with pytest.raises(SystemExit) as exc:
        jsonl.main(["--version"])
    assert exc.value.code == 0


def test_version_when_package_metadata_unavailable(monkeypatch):
    def raise_not_found(_distribution):
        raise importlib.metadata.PackageNotFoundError

    monkeypatch.setattr(importlib.metadata, "version", raise_not_found)

    assert jsonl._get_version() == "unknown"


def test_help():
    with pytest.raises(SystemExit) as exc:
        jsonl.main(["--help"])
    assert exc.value.code == 0


def test_broken_pipe_during_write_returns_runtime_error(monkeypatch):
    set_stdin(monkeypatch, "[1]\n")
    redirected = []

    def raise_broken_pipe(_records, _outfile, _encoder_kwargs):
        raise BrokenPipeError

    monkeypatch.setattr(jsonl, "_cli_write", raise_broken_pipe)
    monkeypatch.setattr(jsonl, "_redirect_stdout_to_devnull", lambda: redirected.append(True))

    assert jsonl.main([]) == 3
    assert redirected == [True]


def test_broken_pipe_during_final_flush_returns_runtime_error(monkeypatch):
    set_stdin(monkeypatch, "[1]\n")
    monkeypatch.setattr(jsonl.sys, "stdout", FlushErrorStream(BrokenPipeError()))
    redirected = []
    monkeypatch.setattr(jsonl, "_redirect_stdout_to_devnull", lambda: redirected.append(True))

    assert jsonl.main([]) == 3
    assert redirected == [True]


def test_non_pipe_error_during_final_flush_is_reported(monkeypatch, capsys):
    set_stdin(monkeypatch, "[1]\n")
    monkeypatch.setattr(jsonl.sys, "stdout", FlushErrorStream(OSError(errno.EIO, "flush failed")))

    assert jsonl.main([]) == 3
    assert "flush failed" in capsys.readouterr().err


def test_redirect_stdout_to_devnull_closes_temporary_descriptor(monkeypatch):
    calls = []
    monkeypatch.setattr(jsonl.sys, "stdout", types.SimpleNamespace(fileno=lambda: 1))
    monkeypatch.setattr(jsonl.os, "open", lambda path, flags: 10)
    monkeypatch.setattr(jsonl.os, "dup2", lambda source, destination: calls.append(("dup2", source, destination)))
    monkeypatch.setattr(jsonl.os, "close", lambda descriptor: calls.append(("close", descriptor)))

    jsonl._redirect_stdout_to_devnull()

    assert calls == [("dup2", 10, 1), ("close", 10)]


@pytest.mark.parametrize("data", [b'{"value": 1}\n', b'{"value": 1}\nNOPE\n'])
def test_broken_pipe_is_handled_before_interpreter_shutdown(data):
    process = subprocess.Popen(
        [sys.executable, "-m", "jsonl"],
        cwd=os.path.dirname(os.path.dirname(__file__)),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.stdout.close()
    process.stdin.write(data)
    process.stdin.close()
    stderr = process.stderr.read()

    assert process.wait() == 3
    assert b"Exception ignored" not in stderr
