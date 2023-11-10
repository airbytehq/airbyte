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
from airbyte_cdk.sources.streams.concurrent.abstract_stream import AbstractStream
from airbyte_cdk.sources.streams.concurrent.partition_enqueuer import PartitionEnqueuer
from airbyte_cdk.sources.streams.concurrent.partitions.partition import Partition

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

    handler = QueueItemHandler(
        streams_currently_generating_partitions,
        stream_instances_to_read_from,
        partition_enqueuer,
        thread_pool_manager,
        streams_to_partitions,
        record_counter,
        stream_to_instance_map,
        logger,
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

    handler = QueueItemHandler(
        streams_currently_generating_partitions,
        stream_instances_to_read_from,
        partition_enqueuer,
        thread_pool_manager,
        streams_to_partitions,
        record_counter,
        stream_to_instance_map,
        logger,
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
