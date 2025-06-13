
import jsonl
import tests


def test_empty():
    assert not jsonl.dumps(())


def test_iter_data():
    result = jsonl.dumps(iter(tests.data))
    assert result == tests.string_data
