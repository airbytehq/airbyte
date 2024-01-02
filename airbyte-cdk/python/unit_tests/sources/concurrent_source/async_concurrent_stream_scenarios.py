#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging

from airbyte_cdk.sources.message import InMemoryMessageRepository
from unit_tests.sources.scenario_based.scenario_builder import TestScenarioBuilder
from unit_tests.sources.streams.concurrent.scenarios.async_concurrent_stream_source_builder import (
    AlwaysAvailableAvailabilityStrategy,
    ConcurrentSourceBuilder,
    LocalAsyncStream,
)

_id_only_stream = LocalAsyncStream(
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
    slices=[[{"id": "1"}, {"id": "2"}]],
)

_id_only_stream_with_primary_key = LocalAsyncStream(
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
    slices=[[{"id": "1"}, {"id": "2"}]],
)

_id_only_stream_multiple_partitions = LocalAsyncStream(
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
    slices=[[{"id": "1"}, {"id": "2"}], [{"id": "3"}, {"id": "4"}]],
)

_id_only_stream_multiple_partitions_concurrency_level_two = LocalAsyncStream(  # TODO: allow concurrency level to be set
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
    slices=[[{"id": "1"}, {"id": "2"}], [{"id": "3"}, {"id": "4"}]],
)

_stream_raising_exception = LocalAsyncStream(
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
    slices=[[{"id": "1"}, ValueError("test exception")]],
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
                LocalAsyncStream(
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
                    slices=[[{"id": "10", "key": "v1"}, {"id": "20", "key": "v2"}]],
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
