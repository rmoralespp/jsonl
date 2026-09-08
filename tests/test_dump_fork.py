# -*- coding: utf-8 -*-
import contextlib
import json
import os
import pathlib
import tempfile

import pytest

import jsonl
import tests


def _tracking_opener(active, open_counts=None, modes=None):
    @contextlib.contextmanager
    def opener(path, **kwargs):
        with jsonl._xopen(path, **kwargs) as fd:
            active.add(path)
            if open_counts is not None:
                open_counts.append(len(active))
            if modes is not None:
                modes.append(kwargs["mode"])
            try:
                yield fd
            finally:
                active.remove(path)

    return opener


@pytest.mark.parametrize(
    "cls, kwargs",
    [
        (json.JSONEncoder, {"ensure_ascii": False, "separators": (", ", ": ")}),
        (None, {}),
    ],
)
@pytest.mark.parametrize("text_mode", (True, False))
def test_iter_data(file_extension, pathlike, text_mode, cls, kwargs):
    with tempfile.TemporaryDirectory() as tmp:
        foo_path = os.path.join(tmp, f"foo{file_extension}")
        var_path = os.path.join(tmp, f"var{file_extension}")
        baz_path = os.path.join(tmp, f"baz{file_extension}")
        if pathlike:
            foo_path = pathlib.Path(foo_path)
            var_path = pathlib.Path(var_path)
            baz_path = pathlib.Path(baz_path)

        path_items = (
            (foo_path, iter(({"foo": 1}, {"ño": 2}))),
            (foo_path, iter(({"extra": True},))),
            (var_path, iter(({"foo": 1}, {"ño": 2}))),
            (baz_path, iter(())),
        )

        jsonl.dump_fork(iter(path_items), text_mode=text_mode, cls=cls, **kwargs)

        assert tests.read_text(foo_path) == '{"foo": 1}\n{"ño": 2}\n{"extra": true}\n'
        assert tests.read_text(var_path) == '{"foo": 1}\n{"ño": 2}\n'
        assert not tests.read_text(baz_path)


@pytest.mark.parametrize("pathlike", (True, False))
@pytest.mark.parametrize("dump_if_empty", (True, False))
def test_empty_data(filepath, dump_if_empty, pathlike):
    filepath = pathlib.Path(filepath) if pathlike else filepath
    path_items = ((filepath, ()),)
    jsonl.dump_fork(iter(path_items), dump_if_empty=dump_if_empty)
    if dump_if_empty:
        assert not tests.read_text(filepath)
    else:
        assert not os.path.exists(filepath)


@pytest.mark.parametrize(
    "path_factory",
    [os.fsencode, tests.BytesPath],
    ids=["bytes", "pathlike-bytes"],
)
def test_bytes_filepath_rejected(filepath, path_factory):
    with pytest.raises(TypeError, match="bytes paths are not supported"):
        jsonl.dump_fork([(path_factory(filepath), tests.data)])


@pytest.mark.parametrize("text_mode", (True, False))
def test_open_files_are_bounded_and_reopened(tmp_dir, file_extension, text_mode):
    paths = [str(tmp_dir / f"partition-{index}{file_extension}") for index in range(4)]
    path_items = [
        (path, [{"batch": batch}])
        for batch in range(2)
        for path in paths
    ]
    active = set()
    open_counts = []
    modes = []

    jsonl.dump_fork(
        path_items,
        opener=_tracking_opener(active, open_counts, modes),
        text_mode=text_mode,
        max_open_files=2,
    )

    assert not active
    assert max(open_counts) == 2
    assert modes == [("wt" if text_mode else "wb")] * 4 + [("at" if text_mode else "ab")] * 4
    for path in paths:
        assert list(jsonl.load(path)) == [{"batch": 0}, {"batch": 1}]


def test_default_open_file_limit(tmp_dir):
    paths = [str(tmp_dir / f"{index}.jsonl") for index in range(jsonl._default_max_open_files + 6)]
    active = set()
    open_counts = []

    jsonl.dump_fork(
        [(path, [{"path": path}]) for path in paths],
        opener=_tracking_opener(active, open_counts),
    )

    assert not active
    assert max(open_counts) == jsonl._default_max_open_files


def test_recently_used_writer_is_not_evicted(tmp_dir):
    first = str(tmp_dir / "first.jsonl")
    second = str(tmp_dir / "second.jsonl")
    third = str(tmp_dir / "third.jsonl")
    active = set()
    modes = []
    path_items = [
        (first, [{"batch": 1}]),
        (second, [{"batch": 1}]),
        (first, [{"batch": 2}]),
        (third, [{"batch": 1}]),
        (second, [{"batch": 2}]),
    ]

    jsonl.dump_fork(
        path_items,
        opener=_tracking_opener(active, modes=modes),
        max_open_files=2,
    )

    assert modes == ["wt", "wt", "wt", "at"]
    assert list(jsonl.load(first)) == [{"batch": 1}, {"batch": 2}]
    assert list(jsonl.load(second)) == [{"batch": 1}, {"batch": 2}]


def test_open_file_limit_can_be_disabled(tmp_dir):
    paths = [str(tmp_dir / f"{index}.jsonl") for index in range(3)]
    active = set()
    open_counts = []

    jsonl.dump_fork(
        [(path, tests.data) for path in paths],
        opener=_tracking_opener(active, open_counts),
        max_open_files=None,
    )

    assert max(open_counts) == len(paths)


@pytest.mark.parametrize(
    "max_open_files, error, message",
    [
        (1.5, TypeError, "max_open_files must be an integer"),
        (0, ValueError, "max_open_files must be greater than zero"),
        (-1, ValueError, "max_open_files must be greater than zero"),
    ],
)
def test_invalid_max_open_files(filepath, max_open_files, error, message):
    with pytest.raises(error, match=message):
        jsonl.dump_fork([(filepath, tests.data)], max_open_files=max_open_files)

    assert not os.path.exists(filepath)


def test_empty_reopened_destination_preserves_previous_data(tmp_dir):
    first = str(tmp_dir / "first.jsonl")
    second = str(tmp_dir / "second.jsonl")
    path_items = [
        (first, [{"batch": 1}]),
        (second, [{"batch": 1}]),
        (first, []),
    ]

    jsonl.dump_fork(path_items, dump_if_empty=False, max_open_files=1)

    assert list(jsonl.load(first)) == [{"batch": 1}]


def test_removed_empty_destination_can_be_reopened(tmp_dir):
    first = str(tmp_dir / "first.jsonl")
    second = str(tmp_dir / "second.jsonl")
    path_items = [
        (first, []),
        (second, [{"batch": 1}]),
        (first, [{"batch": 2}]),
    ]

    jsonl.dump_fork(path_items, dump_if_empty=False, max_open_files=1)

    assert list(jsonl.load(first)) == [{"batch": 2}]


def test_writers_close_after_paths_iteration_fails(tmp_dir):
    active = set()
    first = str(tmp_dir / "first.jsonl")
    second = str(tmp_dir / "second.jsonl")

    def path_items():
        yield (first, [{"batch": 1}])
        yield (second, [{"batch": 1}])
        raise RuntimeError("iteration failed")

    with pytest.raises(RuntimeError, match="iteration failed"):
        jsonl.dump_fork(path_items(), opener=_tracking_opener(active))

    assert not active


def test_writers_close_after_serialization_fails(tmp_dir):
    active = set()
    first = str(tmp_dir / "first.jsonl")
    second = str(tmp_dir / "second.jsonl")

    def encode(value):
        if value.get("invalid"):
            raise RuntimeError("serialization failed")
        return json.dumps(value)

    path_items = [
        (first, [{"batch": 1}]),
        (second, [{"invalid": True}]),
    ]
    with pytest.raises(RuntimeError, match="serialization failed"):
        jsonl.dump_fork(path_items, opener=_tracking_opener(active), cls=encode)

    assert not active


def test_writers_close_after_opening_fails(tmp_dir):
    active = set()
    first = str(tmp_dir / "first.jsonl")
    second = str(tmp_dir / "second.jsonl")
    tracked_open = _tracking_opener(active)

    def opener(path, **kwargs):
        if path == second:
            raise OSError("opening failed")
        return tracked_open(path, **kwargs)

    with pytest.raises(OSError, match="opening failed"):
        jsonl.dump_fork([(first, tests.data), (second, tests.data)], opener=opener)

    assert not active


def test_all_writers_close_when_closing_fails(tmp_dir):
    active = set()
    paths = [str(tmp_dir / f"{index}.jsonl") for index in range(2)]

    @contextlib.contextmanager
    def opener(path, **kwargs):
        with jsonl._xopen(path, **kwargs) as fd:
            active.add(path)
            try:
                yield fd
            finally:
                active.remove(path)
                raise RuntimeError(f"closing failed: {path}")

    with pytest.raises(RuntimeError, match="closing failed"):
        jsonl.dump_fork([(path, tests.data) for path in paths], opener=opener)

    assert not active


def test_serialization_error_is_preserved_when_another_writer_fails_to_close(tmp_dir):
    active = set()
    first = str(tmp_dir / "first.jsonl")
    second = str(tmp_dir / "second.jsonl")

    @contextlib.contextmanager
    def opener(path, **kwargs):
        with jsonl._xopen(path, **kwargs) as fd:
            active.add(path)
            try:
                yield fd
            finally:
                active.remove(path)
                if path == first:
                    raise RuntimeError("closing failed")

    def encode(value):
        if value.get("invalid"):
            raise ValueError("serialization failed")
        return json.dumps(value)

    path_items = [
        (first, [{"batch": 1}]),
        (second, [{"invalid": True}]),
    ]
    with pytest.raises(ValueError, match="serialization failed"):
        jsonl.dump_fork(path_items, opener=opener, cls=encode)

    assert not active
