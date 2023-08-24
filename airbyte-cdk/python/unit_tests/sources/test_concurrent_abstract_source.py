#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from queue import Queue
from typing import Any, Iterable, List, Mapping, Optional, Tuple
from unittest import TestCase
from unittest.mock import Mock, call

from airbyte_cdk.sources.concurrent.concurrent_abstract_source import (
    _SENTINEL,
    ConcurrentAbstractSource,
    Partition,
    PartitionGenerator,
    QueueConsumer,
)
from airbyte_cdk.sources.streams import Stream


class MockConcurrentAbstractSource(ConcurrentAbstractSource):
    def __init__(self, partition_generator, queue_consumer: QueueConsumer, queue: Queue, streams: List[Stream]):
        super().__init__(partition_generator, queue_consumer, queue)
        self._streams = streams

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        pass

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return self._streams


class MockPartitionGenerator(PartitionGenerator):
    def __init__(self, queue: Queue):
        self._queue = queue

    def generate_partitions_for_stream(self, stream: Stream) -> Iterable[Partition]:
        yield from stream.generate_partitions()


class ConcurrentFullRefreshReadTestCase(TestCase):
    def setUp(self):
        self._logger = Mock()
        self._state = None

    def test_read_a_single_stream_with_a_single_partition(self):
        queue: Queue = Mock()
        partition_generator: PartitionGenerator = MockPartitionGenerator(queue)
        queue_consumer: QueueConsumer = QueueConsumer()
        stream = Mock()
        streams = [stream]
        source = MockConcurrentAbstractSource(partition_generator, queue_consumer, queue, streams)
        config = {}
        configured_catalog = Mock()  # FIXME?

        partition = Partition()
        partitions = [partition]

        stream.generate_partitions.return_value = iter(partitions)

        records = [
            {"id": 1, "partition": 1},
            {"id": 2, "partition": 1},
        ]
        stream.read_records.return_value = iter(records)

        queue.get.side_effect = [(partition, stream), _SENTINEL]

        all_messages = list(source.read(self._logger, config, configured_catalog, self._state))

        # partition_generator.generate_partitions_for_stream.assert_called_once_with(stream)
        put_calls = [call((partition, stream)), call(_SENTINEL)]
        queue.put.assert_has_calls(put_calls)
        assert queue.get.call_count == 2

        assert len(all_messages) == 2
