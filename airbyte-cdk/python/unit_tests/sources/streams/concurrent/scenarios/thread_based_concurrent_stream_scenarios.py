#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging

from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams.concurrent.default_stream import DefaultStream
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder
from unit_tests.sources.streams.concurrent.scenarios.thread_based_concurrent_stream_source_builder import (
    AlwaysAvailableAvailabilityStrategy,
    ConcurrentSourceBuilder,
    InMemoryPartition,
    InMemoryPartitionGenerator,
)

_id_only_stream = DefaultStream(
    partition_generator=InMemoryPartitionGenerator(
        [InMemoryPartition("partition1", "stream1", None, [Record({"id": "1"}, "stream1"), Record({"id": "2"}, "stream1")])]
    ),
    name="stream1",
    json_schema={
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
        },
    },
    availability_strategy=AlwaysAvailableAvailabilityStrategy(),
    primary_key=[],
    cursor_field=None,
    logger=logging.getLogger("test_logger"),
)

_id_only_stream_with_slice_logger = DefaultStream(
    partition_generator=InMemoryPartitionGenerator(
        [InMemoryPartition("partition1", "stream1", None, [Record({"id": "1"}, "stream1"), Record({"id": "2"}, "stream1")])]
    ),
    name="stream1",
    json_schema={
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
        },
    },
    availability_strategy=AlwaysAvailableAvailabilityStrategy(),
    primary_key=[],
    cursor_field=None,
    logger=logging.getLogger("test_logger"),
)

_id_only_stream_with_primary_key = DefaultStream(
    partition_generator=InMemoryPartitionGenerator(
        [InMemoryPartition("partition1", "stream1", None, [Record({"id": "1"}, "stream1"), Record({"id": "2"}, "stream1")])]
    ),
    name="stream1",
    json_schema={
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
        },
    },
    availability_strategy=AlwaysAvailableAvailabilityStrategy(),
    primary_key=["id"],
    cursor_field=None,
    logger=logging.getLogger("test_logger"),
)

_id_only_stream_multiple_partitions = DefaultStream(
    partition_generator=InMemoryPartitionGenerator(
        [
            InMemoryPartition("partition1", "stream1", {"p": "1"}, [Record({"id": "1"}, "stream1"), Record({"id": "2"}, "stream1")]),
            InMemoryPartition("partition2", "stream1", {"p": "2"}, [Record({"id": "3"}, "stream1"), Record({"id": "4"}, "stream1")]),
        ]
    ),
    name="stream1",
    json_schema={
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
        },
    },
    availability_strategy=AlwaysAvailableAvailabilityStrategy(),
    primary_key=[],
    cursor_field=None,
    logger=logging.getLogger("test_logger"),
)

_id_only_stream_multiple_partitions_concurrency_level_two = DefaultStream(
    partition_generator=InMemoryPartitionGenerator(
        [
            InMemoryPartition("partition1", "stream1", {"p": "1"}, [Record({"id": "1"}, "stream1"), Record({"id": "2"}, "stream1")]),
            InMemoryPartition("partition2", "stream1", {"p": "2"}, [Record({"id": "3"}, "stream1"), Record({"id": "4"}, "stream1")]),
        ]
    ),
    name="stream1",
    json_schema={
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
        },
    },
    availability_strategy=AlwaysAvailableAvailabilityStrategy(),
    primary_key=[],
    cursor_field=None,
    logger=logging.getLogger("test_logger"),
)

_stream_raising_exception = DefaultStream(
    partition_generator=InMemoryPartitionGenerator(
        [InMemoryPartition("partition1", "stream1", None, [Record({"id": "1"}, "stream1"), ValueError("test exception")])]
    ),
    name="stream1",
    json_schema={
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
        },
    },
    availability_strategy=AlwaysAvailableAvailabilityStrategy(),
    primary_key=[],
    cursor_field=None,
    logger=logging.getLogger("test_logger"),
)

test_concurrent_cdk_single_stream = (
    TestScenarioBuilder()
    .set_name("test_concurrent_cdk_single_stream")
    .set_config({})
    .set_source_builder(
        ConcurrentSourceBuilder()
        .set_streams(
            [
                _id_only_stream,
            ]
        )
        .set_message_repository(InMemoryMessageRepository())
    )
    .set_expected_records(
        [
            {"data": {"id": "1"}, "stream": "stream1"},
            {"data": {"id": "2"}, "stream": "stream1"},
        ]
    )
    .set_expected_logs(
        {
            "read": [
                {"level": "INFO", "message": "Starting syncing"},
                {"level": "INFO", "message": "Marking stream stream1 as STARTED"},
                {"level": "INFO", "message": "Syncing stream: stream1"},
                {"level": "INFO", "message": "Marking stream stream1 as RUNNING"},
                {"level": "INFO", "message": "Read 2 records from stream1 stream"},
                {"level": "INFO", "message": "Marking stream stream1 as STOPPED"},
                {"level": "INFO", "message": "Finished syncing stream1"},
                {"level": "INFO", "message": "Finished syncing"},
            ]
        }
    )
    .set_log_levels({"ERROR", "WARN", "WARNING", "INFO", "DEBUG"})
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh"],
                }
            ]
        }
    )
    .build()
)

test_concurrent_cdk_single_stream_with_primary_key = (
    TestScenarioBuilder()
    .set_name("test_concurrent_cdk_single_stream_with_primary_key")
    .set_config({})
    .set_source_builder(
        ConcurrentSourceBuilder()
        .set_streams(
            [
                _id_only_stream_with_primary_key,
            ]
        )
        .set_message_repository(InMemoryMessageRepository())
    )
    .set_expected_records(
        [
            {"data": {"id": "1"}, "stream": "stream1"},
            {"data": {"id": "2"}, "stream": "stream1"},
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh"],
                    "source_defined_primary_key": [["id"]],
                }
            ]
        }
    )
    .build()
)

test_concurrent_cdk_multiple_streams = (
    TestScenarioBuilder()
    .set_name("test_concurrent_cdk_multiple_streams")
    .set_config({})
    .set_source_builder(
        ConcurrentSourceBuilder()
        .set_streams(
            [
                _id_only_stream,
                DefaultStream(
                    partition_generator=InMemoryPartitionGenerator(
                        [
                            InMemoryPartition(
                                "partition1",
                                "stream2",
                                None,
                                [Record({"id": "10", "key": "v1"}, "stream2"), Record({"id": "20", "key": "v2"}, "stream2")],
                            )
                        ]
                    ),
                    name="stream2",
                    json_schema={
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                            "key": {"type": ["null", "string"]},
                        },
                    },
                    availability_strategy=AlwaysAvailableAvailabilityStrategy(),
                    primary_key=[],
                    cursor_field=None,
                    logger=logging.getLogger("test_logger"),
                ),
            ]
        )
        .set_message_repository(InMemoryMessageRepository())
    )
    .set_expected_records(
        [
            {"data": {"id": "1"}, "stream": "stream1"},
            {"data": {"id": "2"}, "stream": "stream1"},
            {"data": {"id": "10", "key": "v1"}, "stream": "stream2"},
            {"data": {"id": "20", "key": "v2"}, "stream": "stream2"},
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh"],
                },
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                            "key": {"type": ["null", "string"]},
                        },
                    },
                    "name": "stream2",
                    "supported_sync_modes": ["full_refresh"],
                },
            ]
        }
    )
    .build()
)

test_concurrent_cdk_partition_raises_exception = (
    TestScenarioBuilder()
    .set_name("test_concurrent_partition_raises_exception")
    .set_config({})
    .set_source_builder(
        ConcurrentSourceBuilder()
        .set_streams(
            [
                _stream_raising_exception,
            ]
        )
        .set_message_repository(InMemoryMessageRepository())
    )
    .set_expected_records(
        [
            {"data": {"id": "1"}, "stream": "stream1"},
        ]
    )
    .set_expected_read_error(ValueError, "test exception")
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh"],
                }
            ]
        }
    )
    .build()
)

test_concurrent_cdk_single_stream_multiple_partitions = (
    TestScenarioBuilder()
    .set_name("test_concurrent_cdk_single_stream_multiple_partitions")
    .set_config({})
    .set_source_builder(
        ConcurrentSourceBuilder()
        .set_streams(
            [
                _id_only_stream_multiple_partitions,
            ]
        )
        .set_message_repository(InMemoryMessageRepository())
    )
    .set_expected_records(
        [
            {"data": {"id": "1"}, "stream": "stream1"},
            {"data": {"id": "2"}, "stream": "stream1"},
            {"data": {"id": "3"}, "stream": "stream1"},
            {"data": {"id": "4"}, "stream": "stream1"},
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh"],
                }
            ]
        }
    )
    .build()
)

test_concurrent_cdk_single_stream_multiple_partitions_concurrency_level_two = (
    TestScenarioBuilder()
    .set_name("test_concurrent_cdk_single_stream_multiple_partitions_concurrency_level_2")
    .set_config({})
    .set_source_builder(
        ConcurrentSourceBuilder()
        .set_streams(
            [
                _id_only_stream_multiple_partitions_concurrency_level_two,
            ]
        )
        .set_message_repository(InMemoryMessageRepository())
    )
    .set_expected_records(
        [
            {"data": {"id": "1"}, "stream": "stream1"},
            {"data": {"id": "2"}, "stream": "stream1"},
            {"data": {"id": "3"}, "stream": "stream1"},
            {"data": {"id": "4"}, "stream": "stream1"},
        ]
    )
    .set_expected_catalog(
        {
            "streams": [
                {
                    "json_schema": {
                        "type": "object",
                        "properties": {
                            "id": {"type": ["null", "string"]},
                        },
                    },
                    "name": "stream1",
                    "supported_sync_modes": ["full_refresh"],
                }
            ]
        }
    )
    .build()
)
