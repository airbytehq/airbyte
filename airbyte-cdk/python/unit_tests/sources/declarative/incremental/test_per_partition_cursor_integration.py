#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.declarative.incremental.per_partition_cursor import PerPartitionStreamSlice
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.streams.http import HttpStream

CURSOR_FIELD = "cursor_field"
SYNC_MODE = SyncMode.incremental


class ManifestBuilder:
    def __init__(self):
        self._incremental_sync = None
        self._partition_router = None

    def with_list_partition_router(self, cursor_field, partitions):
        self._partition_router = {
            "type": "ListPartitionRouter",
            "cursor_field": cursor_field,
            "values": partitions,
        }
        return self

    def with_incremental_sync(self, start_datetime, end_datetime, datetime_format, cursor_field, step, cursor_granularity):
        self._incremental_sync = {
            "type": "DatetimeBasedCursor",
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "datetime_format": datetime_format,
            "cursor_field": cursor_field,
            "step": step,
            "cursor_granularity": cursor_granularity
        }
        return self

    def build(self):
        manifest = {
            "version": "0.34.2",
            "type": "DeclarativeSource",
            "check": {
                "type": "CheckStream",
                "stream_names": [
                    "Rates"
                ]
            },
            "streams": [
                {
                    "type": "DeclarativeStream",
                    "name": "Rates",
                    "primary_key": [],
                    "schema_loader": {
                        "type": "InlineSchemaLoader",
                        "schema": {
                            "$schema": "http://json-schema.org/schema#",
                            "properties": {},
                            "type": "object"
                        }
                    },
                    "retriever": {
                        "type": "SimpleRetriever",
                        "requester": {
                            "type": "HttpRequester",
                            "url_base": "https://api.apilayer.com",
                            "path": "/exchangerates_data/latest",
                            "http_method": "GET",
                        },
                        "record_selector": {
                            "type": "RecordSelector",
                            "extractor": {
                                "type": "DpathExtractor",
                                "field_path": []
                            }
                        },
                    }
                }
            ],
            "spec": {
                "connection_specification": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "required": [],
                    "properties": {},
                    "additionalProperties": True
                },
                "documentation_url": "https://example.org",
                "type": "Spec"
            }
        }
        if self._incremental_sync:
            manifest["streams"][0]["incremental_sync"] = self._incremental_sync
        if self._partition_router:
            manifest["streams"][0]["retriever"]["partition_router"] = self._partition_router
        return manifest


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

    with patch.object(HttpStream, "_read_pages", side_effect=[[{"a record key": "a record value", CURSOR_FIELD: "2022-01-15"}]]):
        list(
            stream_instance.read_records(
                sync_mode=SYNC_MODE,
                stream_slice=PerPartitionStreamSlice({"partition_field": "1"}, {"start_time": "2022-01-01", "end_time": "2022-01-31"}),
                stream_state={"states": []},
                cursor_field=CURSOR_FIELD,
            )
        )

    assert stream_instance.state == {"states": [
        {
            "partition": {"partition_field": "1"},
            "cursor": {CURSOR_FIELD: "2022-01-15"},
        }
    ]}
