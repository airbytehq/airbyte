#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from unittest.mock import MagicMock, patch

from airbyte_cdk.models import (
    AirbyteStateBlob,
    AirbyteStateMessage,
    AirbyteStateType,
    AirbyteStream,
    AirbyteStreamState,
    ConfiguredAirbyteCatalog,
    ConfiguredAirbyteStream,
    DestinationSyncMode,
    StreamDescriptor,
    SyncMode,
)
from airbyte_cdk.sources.declarative.incremental.per_partition_cursor import PerPartitionCursor, StreamSlice
from airbyte_cdk.sources.declarative.manifest_declarative_source import ManifestDeclarativeSource
from airbyte_cdk.sources.declarative.retrievers.simple_retriever import SimpleRetriever
from airbyte_cdk.sources.types import Record
from orjson import orjson

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
            ],
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
            "streams": [{"$ref": "#/definitions/Rates"}, {"$ref": "#/definitions/AnotherStream"}],
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

    stream_slice = StreamSlice(partition={"partition_field": "1"}, cursor_slice={"start_time": "2022-01-01", "end_time": "2022-01-31"})
    with patch.object(
        SimpleRetriever, "_read_pages", side_effect=[[Record({"a record key": "a record value", CURSOR_FIELD: "2022-01-15"}, stream_slice)]]
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

    parent_stream_slice = StreamSlice(partition={}, cursor_slice={"start_time": "2022-01-01", "end_time": "2022-01-31"})

    # This mocks the resulting records of the Rates stream which acts as the parent stream of the SubstreamPartitionRouter being tested
    with patch.object(
        SimpleRetriever,
        "_read_pages",
        side_effect=[
            [Record({"id": "1", CURSOR_FIELD: "2022-01-15"}, parent_stream_slice)],
            [Record({"id": "2", CURSOR_FIELD: "2022-01-15"}, parent_stream_slice)],
        ],
    ):
        slices = list(stream_instance.stream_slices(sync_mode=SYNC_MODE))
        assert list(slices) == [
            StreamSlice(
                partition={
                    "parent_id": "1",
                    "parent_slice": {},
                },
                cursor_slice={"start_time": "2022-01-01", "end_time": "2022-01-31"},
            ),
            StreamSlice(
                partition={
                    "parent_id": "1",
                    "parent_slice": {},
                },
                cursor_slice={"start_time": "2022-02-01", "end_time": "2022-02-28"},
            ),
            StreamSlice(
                partition={
                    "parent_id": "2",
                    "parent_slice": {},
                },
                cursor_slice={"start_time": "2022-01-01", "end_time": "2022-01-31"},
            ),
            StreamSlice(
                partition={
                    "parent_id": "2",
                    "parent_slice": {},
                },
                cursor_slice={"start_time": "2022-02-01", "end_time": "2022-02-28"},
            ),
        ]


def test_partition_limitation():
    source = ManifestDeclarativeSource(
        source_config=ManifestBuilder()
        .with_list_partition_router("Rates", "partition_field", ["1", "2", "3"])
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

    partition_slices = [
        StreamSlice(partition={"partition_field": "1"}, cursor_slice={}),
        StreamSlice(partition={"partition_field": "2"}, cursor_slice={}),
        StreamSlice(partition={"partition_field": "3"}, cursor_slice={}),
    ]

    records_list = [
        [
            Record({"a record key": "a record value", CURSOR_FIELD: "2022-01-15"}, partition_slices[0]),
            Record({"a record key": "a record value", CURSOR_FIELD: "2022-01-16"}, partition_slices[0]),
        ],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-02-15"}, partition_slices[0])],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-01-16"}, partition_slices[1])],
        [],
        [],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-02-17"}, partition_slices[2])],
    ]

    configured_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="Rates", json_schema={}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream])

    initial_state = [
        AirbyteStateMessage(
            type=AirbyteStateType.STREAM,
            stream=AirbyteStreamState(
                stream_descriptor=StreamDescriptor(name="post_comment_votes", namespace=None),
                stream_state=AirbyteStateBlob(
                    {
                        "states": [
                            {
                                "partition": {"partition_field": "1"},
                                "cursor": {CURSOR_FIELD: "2022-01-01"},
                            },
                            {
                                "partition": {"partition_field": "2"},
                                "cursor": {CURSOR_FIELD: "2022-01-02"},
                            },
                            {
                                "partition": {"partition_field": "3"},
                                "cursor": {CURSOR_FIELD: "2022-01-03"},
                            },
                        ]
                    }
                ),
            ),
        )
    ]
    logger = MagicMock()

    # with patch.object(PerPartitionCursor, "stream_slices", return_value=partition_slices):
    with patch.object(SimpleRetriever, "_read_pages", side_effect=records_list):
        with patch.object(PerPartitionCursor, "DEFAULT_MAX_PARTITIONS_NUMBER", 2):
            output = list(source.read(logger, {}, catalog, initial_state))

    # assert output_data == expected_records
    final_state = [orjson.loads(orjson.dumps(message.state.stream.stream_state)) for message in output if message.state]
    assert final_state[-1] == {
        "states": [
            {
                "partition": {"partition_field": "2"},
                "cursor": {CURSOR_FIELD: "2022-01-16"},
            },
            {
                "partition": {"partition_field": "3"},
                "cursor": {CURSOR_FIELD: "2022-02-17"},
            },
        ]
    }
