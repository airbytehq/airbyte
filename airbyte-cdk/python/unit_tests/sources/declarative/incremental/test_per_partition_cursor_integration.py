#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.incremental.per_partition_cursor import PerPartitionStreamSlice
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.declarative.types import Record
from airbyte_cdk.sources.streams.http import HttpStream
from unit_tests.unit_test_tooling.manifest import ManifestBuilder

CURSOR_FIELD = "cursor_field"
SYNC_MODE = SyncMode.incremental


def test_given_state_for_only_some_partition_when_stream_slices_then_create_slices_using_state_or_start_from_start_datetime():
    source = ManifestDeclarativeSource(
        source_config=ManifestBuilder().with_list_partition_router("partition_field", ["1", "2"]).with_incremental_sync(
                start_datetime="2022-01-01",
                end_datetime="2022-02-28",
                datetime_format="%Y-%m-%d",
                cursor_field=CURSOR_FIELD,
                step="P1M",
                cursor_granularity="P1D",
            ).build()
    )
    stream_instance = source.streams({})[0]
    stream_instance.state = {
        "states": [
            {
                "partition": {"partition_field": "1"},
                "cursor": {CURSOR_FIELD: "2022-02-01"},
            }
        ]
    }

    slices = stream_instance.stream_slices(
        sync_mode=SYNC_MODE,
        stream_state={},
    )

    assert list(slices) == [
        {"partition_field": "1", "start_time": "2022-02-01", "end_time": "2022-02-28"},
        {"partition_field": "2", "start_time": "2022-01-01", "end_time": "2022-01-31"},
        {"partition_field": "2", "start_time": "2022-02-01", "end_time": "2022-02-28"},
    ]


def test_given_record_for_partition_when_read_then_update_state():
    source = ManifestDeclarativeSource(
        source_config=ManifestBuilder().with_list_partition_router("partition_field", ["1", "2"]).with_incremental_sync(
                start_datetime="2022-01-01",
                end_datetime="2022-02-28",
                datetime_format="%Y-%m-%d",
                cursor_field=CURSOR_FIELD,
                step="P1M",
                cursor_granularity="P1D",
            ).build()
    )
    stream_instance = source.streams({})[0]
    list(stream_instance.stream_slices(sync_mode=SYNC_MODE))

    stream_slice = PerPartitionStreamSlice({"partition_field": "1"}, {"start_time": "2022-01-01", "end_time": "2022-01-31"})
    with patch.object(HttpStream, "_read_pages", side_effect=[[Record({"a record key": "a record value", CURSOR_FIELD: "2022-01-15"}, stream_slice)]]):
        list(
            stream_instance.read_records(
                sync_mode=SYNC_MODE,
                stream_slice=stream_slice,
                stream_state={"states": []},
                cursor_field=CURSOR_FIELD,
            )
        )

    assert stream_instance.state == {"states": [
        {
            "partition": {"partition_field": "1"},
            "cursor": {CURSOR_FIELD: "2022-01-31"},
        }
    ]}
