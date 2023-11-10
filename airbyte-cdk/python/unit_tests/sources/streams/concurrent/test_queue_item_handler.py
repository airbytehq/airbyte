#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from unittest.mock import Mock

import freezegun
from airbyte_cdk.models import (
    AirbyteMessage,
    AirbyteRecordMessage,
    AirbyteStream,
    AirbyteStreamStatus,
    AirbyteStreamStatusTraceMessage,
    AirbyteTraceMessage,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
    TraceType,
)
from airbyte_cdk.models import Type as MessageType
from airbyte_cdk.sources.concurrent_source.partition_generation_completed_sentinel import PartitionGenerationCompletedSentinel
from airbyte_cdk.sources.concurrent_source.queue_item_handler import QueueItemHandler
from airbyte_cdk.sources.concurrent_source.thread_pool_manager import ThreadPoolManager
from airbyte_cdk.sources.message import LogMessage, MessageRepository
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partition_reader import PartitionReader
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition
from airbyte_cdk.sources.utils.slice_logger import SliceLogger

_STREAM_NAME = "stream"


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
    messages = handler.on_partition_generation_completed(sentinel)

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
