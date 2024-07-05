#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import patch

from airbyte_cdk.logger import init_logger
from airbyte_cdk.models import ConfiguredAirbyteCatalog, SyncMode, Type
from airbyte_cdk.sources.declarative.incremental.per_partition_cursor import StreamSlice
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.types import Record

CURSOR_FIELD = "cursor_field"
SYNC_MODE = SyncMode.incremental


class ManifestBuilder:
    def __init__(self):
        self._incremental_sync = {}
        self._partition_router = {}
        self._substream_partition_router = {}

    def with_list_partition_router(self, stream_name, cursor_field, partitions):
        self._partition_router[stream_name] = {
            "type": "ListPartitionRouter",
            "cursor_field": cursor_field,
            "values": partitions,
        }
        return self

    def with_substream_partition_router(self, stream_name):
        self._substream_partition_router[stream_name] = {
            "type": "SubstreamPartitionRouter",
            "parent_stream_configs": [
                {
                    "type": "ParentStreamConfig",
                    "stream": "#/definitions/Rates",
                    "parent_key": "id",
                    "partition_field": "parent_id",

                }
            ]
        }
        return self

    def with_incremental_sync(self, stream_name, start_datetime, end_datetime, datetime_format, cursor_field, step, cursor_granularity):
        self._incremental_sync[stream_name] = {
            "type": "DatetimeBasedCursor",
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "datetime_format": datetime_format,
            "cursor_field": cursor_field,
            "step": step,
            "cursor_granularity": cursor_granularity,
        }
        return self

    def build(self):
        manifest = {
            "version": "0.34.2",
            "type": "DeclarativeSource",
            "check": {"type": "CheckStream", "stream_names": ["Rates"]},
            "definitions": {
                "AnotherStream": {
                    "type": "DeclarativeStream",
                    "name": "AnotherStream",
                    "primary_key": [],
                    "schema_loader": {
                        "type": "InlineSchemaLoader",
                        "schema": {"$schema": "http://json-schema.org/schema#", "properties": {"id": {"type": "string"}}, "type": "object"},
                    },
                    "retriever": {
                        "type": "SimpleRetriever",
                        "requester": {
                            "type": "HttpRequester",
                            "url_base": "https://api.apilayer.com",
                            "path": "/exchangerates_data/latest",
                            "http_method": "GET",
                        },
                        "record_selector": {"type": "RecordSelector", "extractor": {"type": "DpathExtractor", "field_path": []}},
                    },
                },
                "Rates": {
                    "type": "DeclarativeStream",
                    "name": "Rates",
                    "primary_key": [],
                    "schema_loader": {
                        "type": "InlineSchemaLoader",
                        "schema": {"$schema": "http://json-schema.org/schema#", "properties": {}, "type": "object"},
                    },
                    "retriever": {
                        "type": "SimpleRetriever",
                        "requester": {
                            "type": "HttpRequester",
                            "url_base": "https://api.apilayer.com",
                            "path": "/exchangerates_data/latest",
                            "http_method": "GET",
                        },
                        "record_selector": {"type": "RecordSelector", "extractor": {"type": "DpathExtractor", "field_path": []}},
                    },
                },
            },
            "streams": [
                {"$ref": "#/definitions/Rates"},
                {"$ref": "#/definitions/AnotherStream"}
            ],
            "spec": {
                "connection_specification": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "required": [],
                    "properties": {},
                    "additionalProperties": True,
                },
                "documentation_url": "https://example.org",
                "type": "Spec",
            },
        }
        for stream_name, incremental_sync_definition in self._incremental_sync.items():
            manifest["definitions"][stream_name]["incremental_sync"] = incremental_sync_definition
        for stream_name, partition_router_definition in self._partition_router.items():
            manifest["definitions"][stream_name]["retriever"]["partition_router"] = partition_router_definition
        for stream_name, partition_router_definition in self._substream_partition_router.items():
            manifest["definitions"][stream_name]["retriever"]["partition_router"] = partition_router_definition
        return manifest


def test_given_state_for_only_some_partition_when_stream_slices_then_create_slices_using_state_or_start_from_start_datetime():
    source = ManifestDeclarativeSource(
        source_config=ManifestBuilder()
        .with_list_partition_router("Rates", "partition_field", ["1", "2"])
        .with_incremental_sync(
            "Rates",
            start_datetime="2022-01-01",
            end_datetime="2022-02-28",
            datetime_format="%Y-%m-%d",
            cursor_field=CURSOR_FIELD,
            step="P1M",
            cursor_granularity="P1D",
        )
        .build()
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
        source_config=ManifestBuilder()
        .with_list_partition_router("Rates", "partition_field", ["1", "2"])
        .with_incremental_sync(
            "Rates",
            start_datetime="2022-01-01",
            end_datetime="2022-02-28",
            datetime_format="%Y-%m-%d",
            cursor_field=CURSOR_FIELD,
            step="P1M",
            cursor_granularity="P1D",
        )
        .build()
    )
    stream_instance = source.streams({})[0]
    list(stream_instance.stream_slices(sync_mode=SYNC_MODE))

    stream_slice = StreamSlice(partition={"partition_field": "1"},
                               cursor_slice={"start_time": "2022-01-01", "end_time": "2022-01-31"})
    with patch.object(
            SimpleRetriever, "_read_pages",
            side_effect=[[Record({"a record key": "a record value", CURSOR_FIELD: "2022-01-15"}, stream_slice)]]
    ):
        list(
            stream_instance.read_records(
                sync_mode=SYNC_MODE,
                stream_slice=stream_slice,
                stream_state={"states": []},
                cursor_field=CURSOR_FIELD,
            )
        )

    assert stream_instance.state == {
        "states": [
            {
                "partition": {"partition_field": "1"},
                "cursor": {CURSOR_FIELD: "2022-01-15"},
            }
        ]
    }


def test_substream_without_input_state():
    test_source = ManifestDeclarativeSource(
        source_config=ManifestBuilder()
        .with_substream_partition_router("AnotherStream")
        .with_incremental_sync(
            "Rates",
            start_datetime="2022-01-01",
            end_datetime="2022-02-28",
            datetime_format="%Y-%m-%d",
            cursor_field=CURSOR_FIELD,
            step="P1M",
            cursor_granularity="P1D",
        )
        .with_incremental_sync(
            "AnotherStream",
            start_datetime="2022-01-01",
            end_datetime="2022-02-28",
            datetime_format="%Y-%m-%d",
            cursor_field=CURSOR_FIELD,
            step="P1M",
            cursor_granularity="P1D",
        )
        .build()
    )

    stream_instance = test_source.streams({})[1]

    stream_slice = StreamSlice(partition={"parent_id": "1"},
                               cursor_slice={"start_time": "2022-01-01", "end_time": "2022-01-31"})

    with patch.object(
            SimpleRetriever, "_read_pages", side_effect=[[Record({"id": "1", CURSOR_FIELD: "2022-01-15"}, stream_slice)],
                                                         [Record({"id": "2", CURSOR_FIELD: "2022-01-15"}, stream_slice)]]
    ):
        slices = list(stream_instance.stream_slices(sync_mode=SYNC_MODE))
        assert list(slices) == [
            StreamSlice(partition={"parent_id": "1", "parent_slice": {}, },
                        cursor_slice={"start_time": "2022-01-01", "end_time": "2022-01-31"}),
            StreamSlice(partition={"parent_id": "1", "parent_slice": {}, },
                        cursor_slice={"start_time": "2022-02-01", "end_time": "2022-02-28"}),
            StreamSlice(partition={"parent_id": "2", "parent_slice": {}, },
                        cursor_slice={"start_time": "2022-01-01", "end_time": "2022-01-31"}),
            StreamSlice(partition={"parent_id": "2", "parent_slice": {}, },
                        cursor_slice={"start_time": "2022-02-01", "end_time": "2022-02-28"}),
        ]


def test_substream_with_legacy_input_state():
    source = ManifestDeclarativeSource(
        source_config=ManifestBuilder()
        .with_substream_partition_router("AnotherStream")
        .with_incremental_sync(
            "Rates",
            start_datetime="2022-01-01",
            end_datetime="2022-02-28",
            datetime_format="%Y-%m-%d",
            cursor_field=CURSOR_FIELD,
            step="P1M",
            cursor_granularity="P1D",
        )
        .with_incremental_sync(
            "AnotherStream",
            start_datetime="2022-01-01",
            end_datetime="2022-02-28",
            datetime_format="%Y-%m-%d",
            cursor_field=CURSOR_FIELD,
            step="P1M",
            cursor_granularity="P1D",
        )
        .build()
    )

    stream_instance = source.streams({})[1]

    input_state = {
        "states": [
            {
                "partition": {"item_id": "an_item_id",
                              "parent_slice": {"end_time": "1629640663", "start_time": "1626962264"},
                              },
                "cursor": {
                    "updated_at": "1709058818"
                }
            }
        ]
    }
    stream_instance.state = input_state

    stream_slice = StreamSlice(partition={"parent_id": "1"},
                               cursor_slice={"start_time": "2022-01-01", "end_time": "2022-01-31"})

    logger = init_logger("airbyte")
    configured_catalog = ConfiguredAirbyteCatalog(
        streams=[
            {
                "stream": {"name": "AnotherStream", "json_schema": {}, "supported_sync_modes": ["incremental"]},
                "sync_mode": "incremental",
                "destination_sync_mode": "overwrite",
            },
        ]
    )

    with patch.object(
            SimpleRetriever, "_read_pages", side_effect=[
                [Record({"id": "1", CURSOR_FIELD: "2022-01-15"}, stream_slice)],
                [Record({"parent_id": "1", CURSOR_FIELD: "2022-01-15"}, stream_slice)],
                [Record({"id": "2", CURSOR_FIELD: "2022-01-15"}, stream_slice)],
                [Record({"parent_id": "2", CURSOR_FIELD: "2022-01-15"}, stream_slice)]
            ]
    ):
        messages = list(source.read(logger, {}, configured_catalog, input_state))

        output_state_message = [message for message in messages if message.type == Type.STATE][0]

        expected_state = {"states": [
            {
                "cursor": {
                    CURSOR_FIELD: "2022-01-15"
                },
                "partition": {"parent_id": "1", "parent_slice": {}}
            }
        ]}

        assert output_state_message.state.stream.stream_state == expected_state
