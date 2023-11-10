#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
import unittest
from unittest.mock import Mock

import freezegun
from airbyte_cdk.models import (
    AirbyteLogMessage,
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
)
from airbyte_cdk.models import Level as LogLevel
from airbyte_cdk.models import StreamDescriptor, SyncMode, TraceType
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.concurrent_source.queue_item_handler import QueueItemHandler
from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.message import LogMessage, MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.partitions.types import PartitionCompleteSentinel
from airbyte_cdk.sources.utils.slice_logger import SliceLogger

_STREAM_NAME = "stream"
_ANOTHER_STREAM_NAME = "stream2"


def test_handle_partition_done_no_other_streams_to_generate_partitions_for():
    streams_currently_generating_partitions = [_STREAM_NAME]
    stream_instances_to_read_from = []
    partition_enqueuer = Mock(spec=PartitionEnqueuer)
    thread_pool_manager = Mock(spec=ThreadPoolManager)
    partition = Mock(spec=Partition)
    partition.is_closed.return_value = False
    streams_to_partitions = {_STREAM_NAME: {partition}}
    record_counter = {_STREAM_NAME: 0}
    stream_to_instance_map = {}
    logger = Mock(spec=logging.Logger)
    slice_logger = Mock(spec=SliceLogger)
    message_repository = Mock(spec=MessageRepository)
    partition_reader = Mock(spec=PartitionReader)

    handler = QueueItemHandler(
        streams_currently_generating_partitions,
        stream_instances_to_read_from,
        partition_enqueuer,
        thread_pool_manager,
        streams_to_partitions,
        record_counter,
        stream_to_instance_map,
        logger,
        slice_logger,
        message_repository,
        partition_reader,
    )

    stream = Mock(spec=AbstractStream)
    stream.name = _STREAM_NAME
    stream.as_airbyte_stream.return_value = AirbyteStream(
        name=_STREAM_NAME,
        json_schema={},
        supported_sync_modes=[SyncMode.full_refresh],
    )
    stream_to_instance_map[_STREAM_NAME] = stream
    sentinel = PartitionGenerationCompletedSentinel(stream)
    messages = list(handler.on_partition_generation_completed(sentinel))

    expected_messages = []
    assert expected_messages == messages


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_handle_last_stream_partition_done():
    streams_currently_generating_partitions = [_STREAM_NAME]
    stream_instances_to_read_from = []
    partition_enqueuer = Mock(spec=PartitionEnqueuer)
    thread_pool_manager = Mock(spec=ThreadPoolManager)
    partition = Mock(spec=Partition)
    partition.is_closed.return_value = True
    streams_to_partitions = {_STREAM_NAME: {partition}}
    record_counter = {_STREAM_NAME: 0}
    stream_to_instance_map = {}
    logger = Mock(spec=logging.Logger)
    slice_logger = Mock(spec=SliceLogger)
    message_repository = Mock(spec=MessageRepository)
    partition_reader = Mock(spec=PartitionReader)

    handler = QueueItemHandler(
        streams_currently_generating_partitions,
        stream_instances_to_read_from,
        partition_enqueuer,
        thread_pool_manager,
        streams_to_partitions,
        record_counter,
        stream_to_instance_map,
        logger,
        slice_logger,
        message_repository,
        partition_reader,
    )

    stream = Mock(spec=AbstractStream)
    stream.name = _STREAM_NAME
    stream.as_airbyte_stream.return_value = AirbyteStream(
        name=_STREAM_NAME,
        json_schema={},
        supported_sync_modes=[SyncMode.full_refresh],
    )
    stream_to_instance_map[_STREAM_NAME] = stream
    sentinel = PartitionGenerationCompletedSentinel(stream)
    messages = handler.on_partition_generation_completed(sentinel)

    expected_messages = [
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name=_STREAM_NAME), status=AirbyteStreamStatus(AirbyteStreamStatus.COMPLETE)
                ),
            ),
        )
    ]
    assert expected_messages == messages


def test_handle_partition():
    streams_currently_generating_partitions = [_STREAM_NAME]
    stream_instances_to_read_from = []
    partition_enqueuer = Mock(spec=PartitionEnqueuer)
    thread_pool_manager = Mock(spec=ThreadPoolManager)
    partition = Mock(spec=Partition)
    partition.stream_name.return_value = _STREAM_NAME
    partition.is_closed.return_value = True
    streams_to_partitions = {_STREAM_NAME: {partition}}
    record_counter = {_STREAM_NAME: 0}
    stream_to_instance_map = {}
    logger = Mock(spec=logging.Logger)
    slice_logger = Mock(spec=SliceLogger)
    message_repository = Mock(spec=MessageRepository)
    partition_reader = Mock(spec=PartitionReader)

    handler = QueueItemHandler(
        streams_currently_generating_partitions,
        stream_instances_to_read_from,
        partition_enqueuer,
        thread_pool_manager,
        streams_to_partitions,
        record_counter,
        stream_to_instance_map,
        logger,
        slice_logger,
        message_repository,
        partition_reader,
    )

    handler.on_partition(partition)

    thread_pool_manager.submit.assert_called_with(partition_reader.process_partition, partition)
    assert partition in streams_to_partitions[_STREAM_NAME]


def test_handle_partition_emits_log_message_if_it_should_be_logged():
    streams_currently_generating_partitions = [_STREAM_NAME]
    stream_instances_to_read_from = []
    partition_enqueuer = Mock(spec=PartitionEnqueuer)
    thread_pool_manager = Mock(spec=ThreadPoolManager)
    partition = Mock(spec=Partition)
    log_message = Mock(spec=LogMessage)
    partition.to_slice.return_value = log_message
    partition.stream_name.return_value = _STREAM_NAME
    partition.is_closed.return_value = True
    streams_to_partitions = {_STREAM_NAME: {partition}}
    record_counter = {_STREAM_NAME: 0}
    stream_to_instance_map = {}
    logger = Mock(spec=logging.Logger)
    slice_logger = Mock(spec=SliceLogger)
    slice_logger.should_log_slice_message.return_value = True
    slice_logger.create_slice_log_message.return_value = log_message
    message_repository = Mock(spec=MessageRepository)
    partition_reader = Mock(spec=PartitionReader)

    handler = QueueItemHandler(
        streams_currently_generating_partitions,
        stream_instances_to_read_from,
        partition_enqueuer,
        thread_pool_manager,
        streams_to_partitions,
        record_counter,
        stream_to_instance_map,
        logger,
        slice_logger,
        message_repository,
        partition_reader,
    )

    handler.on_partition(partition)

    thread_pool_manager.submit.assert_called_with(partition_reader.process_partition, partition)
    message_repository.emit_message.assert_called_with(log_message)
    assert partition in streams_to_partitions[_STREAM_NAME]


def test_handle_on_partition_complete_sentinel_with_messages_from_repository():
    streams_currently_generating_partitions = [_STREAM_NAME]
    stream_instances_to_read_from = []
    partition_enqueuer = Mock(spec=PartitionEnqueuer)
    thread_pool_manager = Mock(spec=ThreadPoolManager)
    partition = Mock(spec=Partition)
    log_message = Mock(spec=LogMessage)
    partition.to_slice.return_value = log_message
    partition.stream_name.return_value = _STREAM_NAME
    partition.is_closed.return_value = True
    streams_to_partitions = {_STREAM_NAME: {partition}}
    record_counter = {_STREAM_NAME: 0}
    stream_to_instance_map = {}
    logger = Mock(spec=logging.Logger)
    slice_logger = Mock(spec=SliceLogger)
    slice_logger.should_log_slice_message.return_value = True
    slice_logger.create_slice_log_message.return_value = log_message
    message_repository = Mock(spec=MessageRepository)
    partition_reader = Mock(spec=PartitionReader)

    handler = QueueItemHandler(
        streams_currently_generating_partitions,
        stream_instances_to_read_from,
        partition_enqueuer,
        thread_pool_manager,
        streams_to_partitions,
        record_counter,
        stream_to_instance_map,
        logger,
        slice_logger,
        message_repository,
        partition_reader,
    )

    sentinel = PartitionCompleteSentinel(partition)

    message_repository.consume_queue.return_value = [
        AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=LogLevel.INFO, message="message emitted from the repository"))
    ]

    messages = list(handler.on_partition_complete_sentinel(sentinel))

    expected_messages = [
        AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=LogLevel.INFO, message="message emitted from the repository"))
    ]
    assert expected_messages == messages

    partition.close.assert_called_once()


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_handle_on_partition_complete_sentinel_yields_status_message_if_the_stream_is_done():
    streams_currently_generating_partitions = [_STREAM_NAME]
    stream_instances_to_read_from = []
    partition_enqueuer = Mock(spec=PartitionEnqueuer)
    thread_pool_manager = Mock(spec=ThreadPoolManager)
    partition = Mock(spec=Partition)
    log_message = Mock(spec=LogMessage)
    partition.to_slice.return_value = log_message
    partition.stream_name.return_value = _STREAM_NAME
    partition.is_closed.return_value = True
    streams_to_partitions = {_STREAM_NAME: {partition}}
    record_counter = {_STREAM_NAME: 0}
    stream_to_instance_map = {}
    logger = Mock(spec=logging.Logger)
    slice_logger = Mock(spec=SliceLogger)
    slice_logger.should_log_slice_message.return_value = True
    slice_logger.create_slice_log_message.return_value = log_message
    message_repository = Mock(spec=MessageRepository)
    message_repository.consume_queue.return_value = []
    partition_reader = Mock(spec=PartitionReader)

    handler = QueueItemHandler(
        streams_currently_generating_partitions,
        stream_instances_to_read_from,
        partition_enqueuer,
        thread_pool_manager,
        streams_to_partitions,
        record_counter,
        stream_to_instance_map,
        logger,
        slice_logger,
        message_repository,
        partition_reader,
    )

    stream = Mock(spec=AbstractStream)
    stream.name = _STREAM_NAME
    stream.as_airbyte_stream.return_value = AirbyteStream(
        name=_STREAM_NAME,
        json_schema={},
        supported_sync_modes=[SyncMode.full_refresh],
    )
    stream_to_instance_map[_STREAM_NAME] = stream

    sentinel = PartitionCompleteSentinel(partition)

    # Remove the stream from the list of currently generating to mark it as done
    handler._streams_currently_generating_partitions = []

    messages = list(handler.on_partition_complete_sentinel(sentinel))

    expected_messages = [
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(
                        name=_STREAM_NAME,
                    ),
                    status=AirbyteStreamStatus.COMPLETE,
                ),
                emitted_at=1577836800000.0,
            ),
        )
    ]
    assert expected_messages == messages
    partition.close.assert_called_once()


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_handle_on_partition_complete_sentinel_yields_no_status_message_if_the_stream_is_not_done():
    streams_currently_generating_partitions = [_STREAM_NAME]
    stream_instances_to_read_from = []
    partition_enqueuer = Mock(spec=PartitionEnqueuer)
    thread_pool_manager = Mock(spec=ThreadPoolManager)
    partition = Mock(spec=Partition)
    log_message = Mock(spec=LogMessage)
    partition.to_slice.return_value = log_message
    partition.stream_name.return_value = _STREAM_NAME
    partition.is_closed.return_value = True
    streams_to_partitions = {_STREAM_NAME: {partition}}
    record_counter = {_STREAM_NAME: 0}
    stream_to_instance_map = {}
    logger = Mock(spec=logging.Logger)
    slice_logger = Mock(spec=SliceLogger)
    slice_logger.should_log_slice_message.return_value = True
    slice_logger.create_slice_log_message.return_value = log_message
    message_repository = Mock(spec=MessageRepository)
    message_repository.consume_queue.return_value = []
    partition_reader = Mock(spec=PartitionReader)

    handler = QueueItemHandler(
        streams_currently_generating_partitions,
        stream_instances_to_read_from,
        partition_enqueuer,
        thread_pool_manager,
        streams_to_partitions,
        record_counter,
        stream_to_instance_map,
        logger,
        slice_logger,
        message_repository,
        partition_reader,
    )

    stream = Mock(spec=AbstractStream)
    stream.name = _STREAM_NAME
    stream.as_airbyte_stream.return_value = AirbyteStream(
        name=_STREAM_NAME,
        json_schema={},
        supported_sync_modes=[SyncMode.full_refresh],
    )
    stream_to_instance_map[_STREAM_NAME] = stream

    sentinel = PartitionCompleteSentinel(partition)

    messages = list(handler.on_partition_complete_sentinel(sentinel))

    expected_messages = []
    assert expected_messages == messages
    partition.close.assert_called_once()


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_on_record_no_status_message_no_repository_messge():
    streams_currently_generating_partitions = [_STREAM_NAME]
    stream_instances_to_read_from = []
    partition_enqueuer = Mock(spec=PartitionEnqueuer)
    thread_pool_manager = Mock(spec=ThreadPoolManager)
    partition = Mock(spec=Partition)
    log_message = Mock(spec=LogMessage)
    partition.to_slice.return_value = log_message
    partition.stream_name.return_value = _STREAM_NAME
    partition.is_closed.return_value = True
    streams_to_partitions = {_STREAM_NAME: {partition}}
    record_counter = {_STREAM_NAME: 0}
    stream_to_instance_map = {}
    logger = Mock(spec=logging.Logger)
    slice_logger = Mock(spec=SliceLogger)
    slice_logger.should_log_slice_message.return_value = True
    slice_logger.create_slice_log_message.return_value = log_message
    message_repository = Mock(spec=MessageRepository)
    message_repository.consume_queue.return_value = []
    partition_reader = Mock(spec=PartitionReader)

    handler = QueueItemHandler(
        streams_currently_generating_partitions,
        stream_instances_to_read_from,
        partition_enqueuer,
        thread_pool_manager,
        streams_to_partitions,
        record_counter,
        stream_to_instance_map,
        logger,
        slice_logger,
        message_repository,
        partition_reader,
    )

    stream = Mock(spec=AbstractStream)
    stream.name = _STREAM_NAME
    stream.as_airbyte_stream.return_value = AirbyteStream(
        name=_STREAM_NAME,
        json_schema={},
        supported_sync_modes=[SyncMode.full_refresh],
    )
    stream_to_instance_map[_STREAM_NAME] = stream

    data = {"id": 1, "value": "A"}
    record = Mock(spec=Record)
    record.stream_name = _STREAM_NAME
    record.data = data

    # Simulate a first record
    record_counter[_STREAM_NAME] = 1

    messages = list(handler.on_record(record))

    expected_messages = [
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream=_STREAM_NAME,
                data=data,
                emitted_at=1577836800000,
            ),
        )
    ]
    assert expected_messages == messages


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_on_record_with_repository_messge():
    streams_currently_generating_partitions = [_STREAM_NAME]
    stream_instances_to_read_from = []
    partition_enqueuer = Mock(spec=PartitionEnqueuer)
    thread_pool_manager = Mock(spec=ThreadPoolManager)
    partition = Mock(spec=Partition)
    log_message = Mock(spec=LogMessage)
    partition.to_slice.return_value = log_message
    partition.stream_name.return_value = _STREAM_NAME
    partition.is_closed.return_value = True
    streams_to_partitions = {_STREAM_NAME: {partition}}
    record_counter = {_STREAM_NAME: 0}
    stream_to_instance_map = {}
    logger = Mock(spec=logging.Logger)
    slice_logger = Mock(spec=SliceLogger)
    slice_logger.should_log_slice_message.return_value = True
    slice_logger.create_slice_log_message.return_value = log_message
    message_repository = Mock(spec=MessageRepository)
    message_repository.consume_queue.return_value = [
        AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=LogLevel.INFO, message="message emitted from the repository"))
    ]
    partition_reader = Mock(spec=PartitionReader)

    handler = QueueItemHandler(
        streams_currently_generating_partitions,
        stream_instances_to_read_from,
        partition_enqueuer,
        thread_pool_manager,
        streams_to_partitions,
        record_counter,
        stream_to_instance_map,
        logger,
        slice_logger,
        message_repository,
        partition_reader,
    )

    stream = Mock(spec=AbstractStream)
    stream.name = _STREAM_NAME
    stream.as_airbyte_stream.return_value = AirbyteStream(
        name=_STREAM_NAME,
        json_schema={},
        supported_sync_modes=[SyncMode.full_refresh],
    )
    stream_to_instance_map[_STREAM_NAME] = stream

    data = {"id": 1, "value": "A"}
    record = Mock(spec=Record)
    record.stream_name = _STREAM_NAME
    record.data = data

    # Simulate a first record
    record_counter[_STREAM_NAME] = 1

    messages = list(handler.on_record(record))

    expected_messages = [
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream=_STREAM_NAME,
                data=data,
                emitted_at=1577836800000,
            ),
        ),
        AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=LogLevel.INFO, message="message emitted from the repository")),
    ]
    assert expected_messages == messages
    assert record_counter[_STREAM_NAME] == 2


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_on_record_emits_status_message_on_first_record_no_repository_message():
    streams_currently_generating_partitions = [_STREAM_NAME]
    stream_instances_to_read_from = []
    partition_enqueuer = Mock(spec=PartitionEnqueuer)
    thread_pool_manager = Mock(spec=ThreadPoolManager)
    partition = Mock(spec=Partition)
    log_message = Mock(spec=LogMessage)
    partition.to_slice.return_value = log_message
    partition.stream_name.return_value = _STREAM_NAME
    partition.is_closed.return_value = True
    streams_to_partitions = {_STREAM_NAME: {partition}}
    record_counter = {_STREAM_NAME: 0}
    stream_to_instance_map = {}
    logger = Mock(spec=logging.Logger)
    slice_logger = Mock(spec=SliceLogger)
    slice_logger.should_log_slice_message.return_value = True
    slice_logger.create_slice_log_message.return_value = log_message
    message_repository = Mock(spec=MessageRepository)
    message_repository.consume_queue.return_value = []
    partition_reader = Mock(spec=PartitionReader)

    handler = QueueItemHandler(
        streams_currently_generating_partitions,
        stream_instances_to_read_from,
        partition_enqueuer,
        thread_pool_manager,
        streams_to_partitions,
        record_counter,
        stream_to_instance_map,
        logger,
        slice_logger,
        message_repository,
        partition_reader,
    )

    stream = Mock(spec=AbstractStream)
    stream.name = _STREAM_NAME
    stream.as_airbyte_stream.return_value = AirbyteStream(
        name=_STREAM_NAME,
        json_schema={},
        supported_sync_modes=[SyncMode.full_refresh],
    )
    stream_to_instance_map[_STREAM_NAME] = stream

    data = {"id": 1, "value": "A"}
    record = Mock(spec=Record)
    record.stream_name = _STREAM_NAME
    record.data = data

    messages = list(handler.on_record(record))

    expected_messages = [
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name=_STREAM_NAME), status=AirbyteStreamStatus(AirbyteStreamStatus.RUNNING)
                ),
            ),
        ),
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream=_STREAM_NAME,
                data=data,
                emitted_at=1577836800000,
            ),
        ),
    ]
    assert expected_messages == messages
    assert record_counter[_STREAM_NAME] == 1


@freezegun.freeze_time("2020-01-01T00:00:00")
def test_on_record_emits_status_message_on_first_record_with_repository_message():
    streams_currently_generating_partitions = [_STREAM_NAME]
    stream_instances_to_read_from = []
    partition_enqueuer = Mock(spec=PartitionEnqueuer)
    thread_pool_manager = Mock(spec=ThreadPoolManager)
    partition = Mock(spec=Partition)
    log_message = Mock(spec=LogMessage)
    partition.to_slice.return_value = log_message
    partition.stream_name.return_value = _STREAM_NAME
    partition.is_closed.return_value = True
    streams_to_partitions = {_STREAM_NAME: {partition}}
    record_counter = {_STREAM_NAME: 0}
    stream_to_instance_map = {}
    logger = Mock(spec=logging.Logger)
    slice_logger = Mock(spec=SliceLogger)
    slice_logger.should_log_slice_message.return_value = True
    slice_logger.create_slice_log_message.return_value = log_message
    message_repository = Mock(spec=MessageRepository)
    message_repository.consume_queue.return_value = [
        AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=LogLevel.INFO, message="message emitted from the repository"))
    ]
    partition_reader = Mock(spec=PartitionReader)

    handler = QueueItemHandler(
        streams_currently_generating_partitions,
        stream_instances_to_read_from,
        partition_enqueuer,
        thread_pool_manager,
        streams_to_partitions,
        record_counter,
        stream_to_instance_map,
        logger,
        slice_logger,
        message_repository,
        partition_reader,
    )

    stream = Mock(spec=AbstractStream)
    stream.name = _STREAM_NAME
    stream.as_airbyte_stream.return_value = AirbyteStream(
        name=_STREAM_NAME,
        json_schema={},
        supported_sync_modes=[SyncMode.full_refresh],
    )
    stream_to_instance_map[_STREAM_NAME] = stream

    data = {"id": 1, "value": "A"}
    record = Mock(spec=Record)
    record.stream_name = _STREAM_NAME
    record.data = data

    messages = list(handler.on_record(record))

    expected_messages = [
        AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name=_STREAM_NAME), status=AirbyteStreamStatus(AirbyteStreamStatus.RUNNING)
                ),
            ),
        ),
        AirbyteMessage(
            type=MessageType.RECORD,
            record=AirbyteRecordMessage(
                stream=_STREAM_NAME,
                data=data,
                emitted_at=1577836800000,
            ),
        ),
        AirbyteMessage(type=MessageType.LOG, log=AirbyteLogMessage(level=LogLevel.INFO, message="message emitted from the repository")),
    ]
    assert expected_messages == messages
    assert record_counter[_STREAM_NAME] == 1


class TestQueueItemHandler(unittest.TestCase):
    def setUp(self):
        self._streams_currently_generating_partitions = [_STREAM_NAME]
        self._partition_enqueuer = Mock(spec=PartitionEnqueuer)
        self._thread_pool_manager = Mock(spec=ThreadPoolManager)

        log_message = Mock(spec=LogMessage)

        self._an_open_partition = Mock(spec=Partition)
        self._an_open_partition.is_closed.return_value = False
        self._an_open_partition.to_slice.return_value = log_message
        self._an_open_partition.stream_name.return_value = _STREAM_NAME

        self._a_closed_partition = Mock(spec=Partition)
        self._a_closed_partition.is_closed.return_value = True

        self._record_counter = {_STREAM_NAME: 0, _ANOTHER_STREAM_NAME: 0}
        self._stream_to_instance_map = {}
        self._logger = Mock(spec=logging.Logger)
        self._slice_logger = Mock(spec=SliceLogger)
        self._slice_logger.create_slice_log_message.return_value = log_message
        self._message_repository = Mock(spec=MessageRepository)
        self._message_repository.consume_queue.return_value = []
        self._partition_reader = Mock(spec=PartitionReader)

        self._stream = Mock(spec=AbstractStream)
        self._stream.name = _STREAM_NAME
        self._stream.as_airbyte_stream.return_value = AirbyteStream(
            name=_STREAM_NAME,
            json_schema={},
            supported_sync_modes=[SyncMode.full_refresh],
        )

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_on_exception_stops_streams_and_raises_an_exception(self):
        stream_instances_to_read_from = []
        streams_to_partitions = {_STREAM_NAME: {self._an_open_partition}, _ANOTHER_STREAM_NAME: {self._a_closed_partition}}

        handler = QueueItemHandler(
            self._streams_currently_generating_partitions,
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            streams_to_partitions,
            self._record_counter,
            self._stream_to_instance_map,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        another_stream = Mock(spec=AbstractStream)
        another_stream.name = _STREAM_NAME
        another_stream.as_airbyte_stream.return_value = AirbyteStream(
            name=_ANOTHER_STREAM_NAME,
            json_schema={},
            supported_sync_modes=[SyncMode.full_refresh],
        )
        self._stream_to_instance_map[_STREAM_NAME] = self._stream
        self._stream_to_instance_map[_ANOTHER_STREAM_NAME] = another_stream

        exception = RuntimeError("Something went wrong")

        messages = []

        with self.assertRaises(RuntimeError):
            for m in handler.on_exception(exception):
                messages.append(m)

        expected_message = [
            AirbyteMessage(
                type=MessageType.TRACE,
                trace=AirbyteTraceMessage(
                    type=TraceType.STREAM_STATUS,
                    emitted_at=1577836800000.0,
                    stream_status=AirbyteStreamStatusTraceMessage(
                        stream_descriptor=StreamDescriptor(name=_STREAM_NAME), status=AirbyteStreamStatus(AirbyteStreamStatus.INCOMPLETE)
                    ),
                ),
            )
        ]

        assert messages == expected_message
        self._thread_pool_manager.shutdown.assert_called_once()

    def test_is_done_is_false_if_there_are_any_instances_to_read_from(self):
        stream_instances_to_read_from = [self._stream]
        streams_to_partitions = {_STREAM_NAME: {self._an_open_partition}, _ANOTHER_STREAM_NAME: {self._a_closed_partition}}

        handler = QueueItemHandler(
            self._streams_currently_generating_partitions,
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            streams_to_partitions,
            self._record_counter,
            self._stream_to_instance_map,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        assert not handler.is_done()

    def test_is_done_is_false_if_there_are_streams_still_generating_partitions(self):
        stream_instances_to_read_from = []
        streams_to_partitions = {_STREAM_NAME: {self._an_open_partition}, _ANOTHER_STREAM_NAME: {self._a_closed_partition}}
        self._streams_currently_generating_partitions = [_STREAM_NAME]

        handler = QueueItemHandler(
            self._streams_currently_generating_partitions,
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            streams_to_partitions,
            self._record_counter,
            self._stream_to_instance_map,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        assert not handler.is_done()

    def test_is_done_is_false_if_all_partitions_are_not_closed(self):
        stream_instances_to_read_from = []
        streams_to_partitions = {_STREAM_NAME: {self._an_open_partition}, _ANOTHER_STREAM_NAME: {self._a_closed_partition}}
        self._streams_currently_generating_partitions = []

        handler = QueueItemHandler(
            self._streams_currently_generating_partitions,
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            streams_to_partitions,
            self._record_counter,
            self._stream_to_instance_map,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        assert not handler.is_done()

    def test_is_done_is_true_if_all_partitions_are_closed_and_no_streams_are_generating_partitions_and_none_are_still_to_run(self):
        stream_instances_to_read_from = []
        streams_to_partitions = {_ANOTHER_STREAM_NAME: {self._a_closed_partition}}
        self._streams_currently_generating_partitions = []

        handler = QueueItemHandler(
            self._streams_currently_generating_partitions,
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            streams_to_partitions,
            self._record_counter,
            self._stream_to_instance_map,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        assert handler.is_done()

    @freezegun.freeze_time("2020-01-01T00:00:00")
    def test_start_next_partition_generator(self):
        stream_instances_to_read_from = [self._stream]
        streams_to_partitions = {_STREAM_NAME: {}}
        handler = QueueItemHandler(
            self._streams_currently_generating_partitions,
            stream_instances_to_read_from,
            self._partition_enqueuer,
            self._thread_pool_manager,
            streams_to_partitions,
            self._record_counter,
            self._stream_to_instance_map,
            self._logger,
            self._slice_logger,
            self._message_repository,
            self._partition_reader,
        )

        status_message = handler.start_next_partition_generator()

        assert status_message == AirbyteMessage(
            type=MessageType.TRACE,
            trace=AirbyteTraceMessage(
                type=TraceType.STREAM_STATUS,
                emitted_at=1577836800000.0,
                stream_status=AirbyteStreamStatusTraceMessage(
                    stream_descriptor=StreamDescriptor(name=_STREAM_NAME), status=AirbyteStreamStatus(AirbyteStreamStatus.STARTED)
                ),
            ),
        )

        assert _STREAM_NAME in handler._streams_currently_generating_partitions
        self._thread_pool_manager.submit.assert_called_with(self._partition_enqueuer.generate_partitions, self._stream)
