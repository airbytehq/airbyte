#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import itertools
import threading
import time
from itertools import product
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.utils import concurrent
from airbyte_cdk.utils.concurrent import ConcurrentStreamReader


class StreamException(Exception):
    pass


class Stream:
    max_workers = 5

    def __init__(self, auto_start=True, slice_exception=None):
        self._start = threading.Event()
        self.auto_start = auto_start
        self.slice_exception = slice_exception

    def start(self):
        self._start.set()

    def stream_slices(self, **kwargs):
        if not self.auto_start:
            self._start.wait()

        for _slice in range(1, 11):
            yield _slice
            # for thread context switching
            time.sleep(0.01)
            if self.slice_exception == _slice:
                raise StreamException()

    def read_records(self, *, stream_slice, **kwargs):
        for record in range(1, 11):
            yield stream_slice, record
            # for thread context switching
            time.sleep(0.01)


class StopException(Exception):
    counter = itertools.count()

    def __init__(self):
        next(self.counter)


def test_read_full_refresh():
    stream_instance = Stream()
    stream_instance.logger = MagicMock()
    records = []
    start_time = time.time()
    with ConcurrentStreamReader(stream_instance, MagicMock()) as reader:
        for record in reader:
            records.append(record)

    assert records == list(product(range(1, 11), range(1, 11)))
    assert 0 < time.time() - start_time < 0.25


def test_threads_shutdown(monkeypatch):
    stream_instance = Stream(auto_start=False)
    stream_instance.logger = MagicMock()

    monkeypatch.setattr(concurrent, "StopException", StopException)
    monkeypatch.setattr(ConcurrentStreamReader, "TIMEOUT", 0.1)

    reader = ConcurrentStreamReader(stream_instance, MagicMock())
    assert not any([t.is_alive() for t in reader.threads])

    with reader:
        assert all([t.is_alive() for t in reader.threads])

    time.sleep(0.3)
    assert not any([t.is_alive() for t in reader.threads[:-1]])
    # producer thread still alive because Stream.stream_slices method is blocked
    assert reader.threads[-1].is_alive()
    assert next(StopException.counter) == stream_instance.max_workers + 1

    stream_instance.start()
    time.sleep(0.3)

    assert not any([t.is_alive() for t in reader.threads])
    assert next(StopException.counter) == stream_instance.max_workers + 3


def test_throw_exception():
    stream_instance = Stream(slice_exception=3)
    stream_instance.logger = MagicMock()
    with ConcurrentStreamReader(stream_instance, MagicMock()) as reader:
        time.sleep(0.05)
        g = iter(reader)
        with pytest.raises(StreamException):
            next(g)
