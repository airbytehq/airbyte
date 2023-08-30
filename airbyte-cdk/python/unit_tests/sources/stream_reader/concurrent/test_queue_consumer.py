#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import concurrent
import time
from queue import Queue
from unittest import TestCase
from unittest.mock import Mock, call

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.stream_reader.concurrent.queue_consumer import _SENTINEL, QueueConsumer
from airbyte_cdk.sources.stream_reader.concurrent.record import Record
from airbyte_cdk.sources.stream_reader.concurrent.stream_partition import StreamPartition


class QueueConsumerTestCase(TestCase):

    _A_CURSOR_FIELD = ["NESTED", "CURSOR"]

    def setUp(self):
        self._name = "A"
        self._queue = Queue()
        self._queue_consumer = QueueConsumer(self._name)

    def test_queue_consumer_returns_after_reader_a_sentinel_value(self):
        self._queue.put(_SENTINEL)

        records = list(self._queue_consumer.consume_from_queue(self._queue))

        assert len(records) == 0

    def test_queue_consumer_yields_nothing_if_stream_yields_no_records_for_the_partition(self):
        queue = Queue()
        partition = {"partition": 1}

        stream = self._mock_stream([])

        queue.put(StreamPartition(stream, partition, self._A_CURSOR_FIELD))
        queue.put(_SENTINEL)

        actual_records = list(self._queue_consumer.consume_from_queue(queue))

        stream.read_records.assert_has_calls(
            [call(stream_slice=partition, sync_mode=SyncMode.full_refresh, cursor_field=self._A_CURSOR_FIELD)]
        )

        assert len(actual_records) == 0

    def test_queue_consumer_yields_records_from_stream_partition(self):
        partition = {"partition": 1}

        records = [
            {"id": 1, "partition": 1},
            {"id": 2, "partition": 1},
        ]
        stream = self._mock_stream(records)

        self._queue.put(StreamPartition(stream, partition, self._A_CURSOR_FIELD))
        self._queue.put(_SENTINEL)

        stream.read_records.return_value = iter(records)

        actual_records = list(self._queue_consumer.consume_from_queue(self._queue))

        stream.read_records.assert_has_calls(
            [call(stream_slice=partition, sync_mode=SyncMode.full_refresh, cursor_field=self._A_CURSOR_FIELD)]
        )

        expected_records = [Record(r, StreamPartition(stream, partition, self._A_CURSOR_FIELD)) for r in records]

        assert actual_records == expected_records

    def test_queue_consumer_runs_until_it_reads_a_sentinel_value(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(QueueConsumer.consume_from_queue, self._queue_consumer, self._queue)
            time.sleep(0.1)
            assert not future.done()
            self._queue.put(_SENTINEL)
            time.sleep(0.1)
            assert future.done()

    def _mock_stream(self, records):
        stream = Mock()
        stream.read_records.return_value = iter(records)
        return stream
