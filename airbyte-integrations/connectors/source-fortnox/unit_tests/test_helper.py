from source_fortnox.source import signal_last


def test_signal_last_empty():
    it = signal_last([])
    try:
        next(it)
        assert False, "Calling next on the empty iterator should raise a StopIteration exception"
    except StopIteration:
        pass


def test_signal_last_one_element():
    actual = list(signal_last([1]))
    expected = [(True, 1)]
    assert actual == expected


def test_signal_last_three_elements():
    actual = list(signal_last([1, 2, 3]))
    expected = [(False, 1), (False, 2), (True, 3)]
    assert actual == expected
