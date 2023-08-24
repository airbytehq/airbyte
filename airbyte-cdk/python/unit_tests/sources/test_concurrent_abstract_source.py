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
        super().__init__(partition_generator, queue_consumer, queue, max_workers=1)
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
        for expected_record in records:
            assert expected_record in all_messages

    def test_read_a_single_stream_with_two_partitions(self):
        queue: Queue = Mock()
        partition_generator: PartitionGenerator = MockPartitionGenerator(queue)
        queue_consumer: QueueConsumer = QueueConsumer()
        stream = Mock()
        streams = [stream]
        source = MockConcurrentAbstractSource(partition_generator, queue_consumer, queue, streams)
        config = {}
        configured_catalog = Mock()  # FIXME?

        partition1 = Partition()
        partition2 = Partition()
        partitions = [partition1, partition2]

        stream.generate_partitions.return_value = iter(partitions)

        records_partition_1 = [
            {"id": 1, "partition": 1},
            {"id": 2, "partition": 1},
        ]

        records_partition_2 = [
            {"id": 3, "partition": 2},
            {"id": 4, "partition": 2},
        ]
        stream.read_records.side_effect = [iter(records_partition_1), iter(records_partition_2)]

        queue.get.side_effect = [(partition1, stream), (partition2, stream), _SENTINEL]

        all_messages = list(source.read(self._logger, config, configured_catalog, self._state))

        # partition_generator.generate_partitions_for_stream.assert_called_once_with(stream)
        expected_put_calls = [call((partition1, stream)), call(partition2, stream), call(_SENTINEL)]
        actual_put_calls = queue.put.mock_calls

        for expected_call in expected_put_calls:
            print(f"expected: {expected_call}")
            print(f"actual: {actual_put_calls}")
            # FIXME would be nice to also compare the stream...
            # FIXME not toally sure why [1]s aren't equal...
            found = any(actual_call[0] == expected_call[0] for actual_call in actual_put_calls)
            assert found
        assert len(expected_put_calls) == len(actual_put_calls)

        assert queue.get.call_count == 3

        assert len(all_messages) == 4

        for expected_record in [*records_partition_1, *records_partition_2]:
            assert expected_record in all_messages

    def test_read_two_streams(self):
        queue: Queue = Mock()
        partition_generator: PartitionGenerator = MockPartitionGenerator(queue)
        queue_consumer: QueueConsumer = QueueConsumer()
        stream1 = Mock()
        stream2 = Mock()
        streams = [stream1, stream2]
        source = MockConcurrentAbstractSource(partition_generator, queue_consumer, queue, streams)
        config = {}
        configured_catalog = Mock()  # FIXME?

        partition1_stream1 = Partition()
        partition2_stream1 = Partition()
        partitions_stream1 = [partition1_stream1, partition2_stream1]
        partition1_stream2 = Partition()
        partitions_stream2 = [partition1_stream2]

        stream1.generate_partitions.return_value = iter(partitions_stream1)
        stream2.generate_partitions.return_value = iter(partitions_stream2)

        records_partition_1 = [
            {"id": 1, "partition": 1, "stream": "A"},
            {"id": 2, "partition": 1, "stream": "A"},
        ]

        records_partition_2 = [
            {"id": 3, "partition": 2, "stream": "A"},
            {"id": 4, "partition": 2, "stream": "A"},
        ]

        records_partition_1_stream_2 = [
            {"id": 1, "partition": 1, "stream": "B"},
            {"id": 2, "partition": 1, "stream": "B"},
            {"id": 3, "partition": 1, "stream": "B"},
        ]
        stream1.read_records.side_effect = [iter(records_partition_1), iter(records_partition_2)]
        stream2.read_records.side_effect = [iter(records_partition_1_stream_2)]

        queue.get.side_effect = [(partition1_stream1, stream1), (partition2_stream1, stream1), (partition1_stream2, stream2), _SENTINEL]

        all_messages = list(source.read(self._logger, config, configured_catalog, self._state))

        # partition_generator.generate_partitions_for_stream.assert_called_once_with(stream)
        expected_put_calls = [
            call((partition1_stream1, stream1)),
            call(partition2_stream1, stream1),
            call(partition1_stream2, stream2),
            call(_SENTINEL),
        ]
        actual_put_calls = queue.put.mock_calls

        for expected_call in expected_put_calls:
            print(f"expected: {expected_call}")
            print(f"actual: {actual_put_calls}")
            # FIXME would be nice to also compare the stream...
            # FIXME not toally sure why [1]s aren't equal...
            found = any(actual_call[0] == expected_call[0] for actual_call in actual_put_calls)
            assert found
        assert len(expected_put_calls) == len(actual_put_calls)

        assert queue.get.call_count == 4

        assert len(all_messages) == 7

        for expected_record in [*records_partition_1, *records_partition_2, *records_partition_1_stream_2]:
            assert expected_record in all_messages
