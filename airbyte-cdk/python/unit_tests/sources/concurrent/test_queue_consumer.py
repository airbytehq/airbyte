#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import concurrent
import time
from queue import Queue
from unittest.mock import Mock, call

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.concurrent.queue_consumer import _SENTINEL, QueueConsumer


def test_queue_consumer_returns_after_reader_a_sentinel_value():
    name = "A"
    queue_consumer = QueueConsumer(name)

    queue = Queue()
    queue.put(_SENTINEL)

    records = list(queue_consumer.consume_from_queue(queue))

    assert len(records) == 0


def test_queue_consumer_yields_nothing_if_stream_yields_no_records_for_the_partition():
    name = "A"
    queue_consumer = QueueConsumer(name)

    queue = Queue()
    partition = {"partition": 1}
    stream = Mock()
    queue.put((partition, stream))
    queue.put(_SENTINEL)

    stream.read_records.return_value = iter([])

    records = list(queue_consumer.consume_from_queue(queue))
    # FIXME need to pass cursor fieeld..

    stream.read_records.assert_has_calls([call(stream_slice=partition, sync_mode=SyncMode.full_refresh, cursor_field=None)])

    assert len(records) == 0


def test_queue_consumer_yields_records_from_stream_partition():
    name = "A"
    queue_consumer = QueueConsumer(name)

    queue = Queue()
    partition = {"partition": 1}
    stream = Mock()
    queue.put((partition, stream))
    queue.put(_SENTINEL)

    records = [
        {"id": 1, "partition": 1},
        {"id": 2, "partition": 1},
    ]

    stream.read_records.return_value = iter(records)

    actual_records = list(queue_consumer.consume_from_queue(queue))

    stream.read_records.assert_has_calls([call(stream_slice=partition, sync_mode=SyncMode.full_refresh, cursor_field=None)])

    expected_records = [(r, stream) for r in records]

    assert actual_records == expected_records


def test_queue_consumer_runs_until_it_reads_a_sentinel_value():
    name = "A"
    queue_consumer = QueueConsumer(name)

    queue = Queue()

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(QueueConsumer.consume_from_queue, queue_consumer, queue)
        time.sleep(0.1)
        assert not future.done()
        queue.put(_SENTINEL)
        time.sleep(0.1)
        assert future.done()
