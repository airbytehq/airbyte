#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from queue import Queue
from typing import Any, List, Mapping, Optional, Tuple
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
from airbyte_protocol.models import AirbyteMessage, AirbyteRecordMessage
from airbyte_protocol.models import Type as MessageType


class MockConcurrentAbstractSource(ConcurrentAbstractSource):
    def __init__(self, partition_generator, queue_consumer: QueueConsumer, queue: Queue, streams: List[Stream]):
        super().__init__(partition_generator, queue_consumer, queue, max_workers=1)
        self._streams = streams

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        pass

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return self._streams


class ConcurrentFullRefreshReadTestCase(TestCase):
    # FIXME: need a test to confirm there are multiple sentinels added to the queue if there's many workers..
    def setUp(self):
        self._logger = Mock()
        self._configured_catalog = Mock()
        self._state = None

    def _mock_stream(self, name: str, partitions, records_per_partition):
        stream = Mock()
        stream.name = name
        stream.get_json_schema.return_value = {}
        stream.generate_partitions.return_value = iter(partitions)
        stream.read_records.side_effect = [iter(records) for records in records_per_partition]
        return stream

    def _read_messages_with_mocked_emitted_at(self, source):
        config = {}
        all_messages = list(source.read(self._logger, config, self._configured_catalog, self._state))
        for message in all_messages:
            message.record.emitted_at = 1
        return all_messages

    def _verify_output_messages(self, actual_messages, expected_messages):
        for expected_message in expected_messages:
            assert expected_message in actual_messages
        assert len(actual_messages) == len(expected_messages)

    def test_read_a_single_stream_with_a_single_partition(self):
        queue: Queue = Mock()
        partition_generator: PartitionGenerator = PartitionGenerator(queue)
        queue_consumer: QueueConsumer = QueueConsumer()

        partition = Partition()
        partitions = [partition]

        records = [
            {"id": 1, "partition": 1},
            {"id": 2, "partition": 1},
        ]
        records_per_partition = [records]

        stream = self._mock_stream("A", partitions, records_per_partition)
        streams = [stream]
        source = MockConcurrentAbstractSource(partition_generator, queue_consumer, queue, streams)
        queue.get.side_effect = [(partition, stream), _SENTINEL]

        all_messages = self._read_messages_with_mocked_emitted_at(source)

        put_calls = [call((partition, stream)), call(_SENTINEL)]
        queue.put.assert_has_calls(put_calls)
        assert queue.get.call_count == 2

        expected_messages = [
            AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(stream="A", data={"id": 1, "partition": 1}, emitted_at=1)),
            AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(stream="A", data={"id": 2, "partition": 1}, emitted_at=1)),
        ]

        self._verify_output_messages(all_messages, expected_messages)

    def test_read_a_single_stream_with_two_partitions(self):
        queue: Queue = Mock()
        partition_generator: PartitionGenerator = PartitionGenerator(queue)
        queue_consumer: QueueConsumer = QueueConsumer()
        partition1 = Partition()
        partition2 = Partition()
        partitions = [partition1, partition2]

        records_partition_1 = [
            {"id": 1, "partition": 1},
            {"id": 2, "partition": 1},
        ]

        records_partition_2 = [
            {"id": 3, "partition": 2},
            {"id": 4, "partition": 2},
        ]
        records_per_partition = [records_partition_1, records_partition_2]
        stream = self._mock_stream("A", partitions, records_per_partition)
        streams = [stream]
        source = MockConcurrentAbstractSource(partition_generator, queue_consumer, queue, streams)

        stream.read_records.side_effect = [iter(records_partition_1), iter(records_partition_2)]

        queue.get.side_effect = [(partition1, stream), (partition2, stream), _SENTINEL]

        all_messages = self._read_messages_with_mocked_emitted_at(source)

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

        expected_messages = [
            AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(stream="A", data={"id": 1, "partition": 1}, emitted_at=1)),
            AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(stream="A", data={"id": 2, "partition": 1}, emitted_at=1)),
            AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(stream="A", data={"id": 3, "partition": 2}, emitted_at=1)),
            AirbyteMessage(type=MessageType.RECORD, record=AirbyteRecordMessage(stream="A", data={"id": 4, "partition": 2}, emitted_at=1)),
        ]

        self._verify_output_messages(all_messages, expected_messages)

    def test_read_two_streams(self):
        queue: Queue = Mock()
        partition_generator: PartitionGenerator = PartitionGenerator(queue)
        queue_consumer: QueueConsumer = QueueConsumer()

        records_partition_1 = [
            {"id": 1, "partition": 1, "stream": "A"},
            {"id": 2, "partition": 1, "stream": "A"},
        ]

        records_partition_2 = [
            {"id": 3, "partition": 2, "stream": "A"},
            {"id": 4, "partition": 2, "stream": "A"},
        ]
        records_stream1_per_partition = [records_partition_1, records_partition_2]
        records_partition_1_stream_2 = [
            {"id": 1, "partition": 1, "stream": "B"},
            {"id": 2, "partition": 1, "stream": "B"},
            {"id": 3, "partition": 1, "stream": "B"},
        ]
        records_stream2_per_partition = [records_partition_1_stream_2]

        partition1_stream1 = Partition()
        partition2_stream1 = Partition()
        partitions_stream1 = [partition1_stream1, partition2_stream1]
        partition1_stream2 = Partition()
        partitions_stream2 = [partition1_stream2]

        stream1 = self._mock_stream("A", partitions_stream1, records_stream1_per_partition)
        stream2 = self._mock_stream("B", partitions_stream2, records_stream2_per_partition)
        streams = [stream1, stream2]
        source = MockConcurrentAbstractSource(partition_generator, queue_consumer, queue, streams)

        queue.get.side_effect = [(partition1_stream1, stream1), (partition2_stream1, stream1), (partition1_stream2, stream2), _SENTINEL]

        all_messages = self._read_messages_with_mocked_emitted_at(source)

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

        expected_messages = [
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(stream="A", data={"id": 1, "partition": 1, "stream": "A"}, emitted_at=1),
            ),
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(stream="A", data={"id": 2, "partition": 1, "stream": "A"}, emitted_at=1),
            ),
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(stream="A", data={"id": 3, "partition": 2, "stream": "A"}, emitted_at=1),
            ),
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(stream="A", data={"id": 4, "partition": 2, "stream": "A"}, emitted_at=1),
            ),
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(stream="B", data={"id": 1, "partition": 1, "stream": "B"}, emitted_at=1),
            ),
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(stream="B", data={"id": 2, "partition": 1, "stream": "B"}, emitted_at=1),
            ),
            AirbyteMessage(
                type=MessageType.RECORD,
                record=AirbyteRecordMessage(stream="B", data={"id": 3, "partition": 1, "stream": "B"}, emitted_at=1),
            ),
        ]

        self._verify_output_messages(all_messages, expected_messages)
