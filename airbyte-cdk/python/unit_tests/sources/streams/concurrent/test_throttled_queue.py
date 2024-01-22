# Copyright (c) 2023 Airbyte, Inc., all rights reserved.

from queue import Queue
from unittest.mock import Mock

import pytest
from _queue import Empty
from airbyte_cdk.sources.concurrent_source.throttler import Throttler
from airbyte_cdk.sources.streams.concurrent.partitions.throttled_queue import ThrottledQueue

_AN_ITEM = Mock()


def test_new_throttled_queue_is_empty():
    queue = Queue()
    throttler = Mock(spec=Throttler)
    timeout = 100
    throttled_queue = ThrottledQueue(queue, throttler, timeout)

    assert throttled_queue.empty()


def test_throttled_queue_is_not_empty_after_putting_an_item():
    queue = Queue()
    throttler = Mock(spec=Throttler)
    timeout = 100
    throttled_queue = ThrottledQueue(queue, throttler, timeout)

    throttled_queue.put(_AN_ITEM)

    assert not throttled_queue.empty()


def test_throttled_queue_get_returns_item_if_any():
    queue = Queue()
    throttler = Mock(spec=Throttler)
    timeout = 100
    throttled_queue = ThrottledQueue(queue, throttler, timeout)

    throttled_queue.put(_AN_ITEM)
    item = throttled_queue.get()

    assert item == _AN_ITEM
    assert throttled_queue.empty()


def test_throttled_queue_blocks_for_timeout_seconds_if_no_items():
    queue = Mock(spec=Queue)
    throttler = Mock(spec=Throttler)
    timeout = 100
    throttled_queue = ThrottledQueue(queue, throttler, timeout)

    throttled_queue.get()

    assert queue.get.is_called_once_with(block=True, timeout=timeout)


def test_throttled_queue_raises_an_error_if_no_items_after_timeout():
    queue = Queue()
    throttler = Mock(spec=Throttler)
    timeout = 0.001
    throttled_queue = ThrottledQueue(queue, throttler, timeout)

    with pytest.raises(Empty):
        throttled_queue.get()
