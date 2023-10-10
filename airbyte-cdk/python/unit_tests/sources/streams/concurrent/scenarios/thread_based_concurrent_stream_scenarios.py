#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging

from airbyte_cdk.sources.message import InMemoryMessageRepository
from airbyte_cdk.sources.streams.concurrent.partitions.record import Record
from airbyte_cdk.sources.streams.concurrent.thread_based_concurrent_stream import ThreadBasedConcurrentStream
from airbyte_cdk.sources.utils.slice_logger import NeverLogSliceLogger
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder
from unit_tests.sources.streams.concurrent.scenarios.thread_based_concurrent_stream_source_builder import (
    AlwaysAvailableAvailabilityStrategy,
    ConcurrentSourceBuilder,
    InMemoryPartition,
    InMemoryPartitionGenerator,
)

test_concurrent_cdk = (
    TestScenarioBuilder()
    .set_name("test_concurrent_cdk")
    .set_config({})
    .set_source_builder(
        ConcurrentSourceBuilder().set_streams(
            [
                ThreadBasedConcurrentStream(
                    partition_generator=InMemoryPartitionGenerator(
                        [InMemoryPartition("partition1", None, [Record({"id": "1"}), Record({"id": "2"})])]
                    ),
                    max_workers=1,
                    name="stream1",
                    json_schema={},
                    availability_strategy=AlwaysAvailableAvailabilityStrategy(),
                    primary_key=[],
                    cursor_field=None,
                    slice_logger=NeverLogSliceLogger(),
                    logger=logging.getLogger("test_logger"),
                    message_repository=InMemoryMessageRepository(),
                    timeout_seconds=300,
                )
            ]
        )
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
