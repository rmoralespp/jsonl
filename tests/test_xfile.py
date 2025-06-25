import bz2
import gzip
import io
import lzma
import unittest.mock

import jsonl


def test_xfile_object(filepath):
    obj = unittest.mock.Mock()
    with jsonl._xfile(filepath, obj) as result:
        if filepath.endswith(".gz"):
            assert isinstance(result, gzip.GzipFile)
        elif filepath.endswith(".bz2"):
            assert isinstance(result, bz2.BZ2File)
        elif filepath.endswith(".xz"):
            assert isinstance(result, lzma.LZMAFile)
        else:
            assert result is obj


def test_xfile_close(filepath):
    buffer = io.BytesIO()

    with jsonl._xfile(filepath, buffer) as output:
        assert not output.closed
        assert not buffer.closed

    if buffer is output:
        # the output should not close the buffer because it is not responsible for closing it.
        assert not buffer.closed
    else:
        assert output.closed
        assert not buffer.closed


