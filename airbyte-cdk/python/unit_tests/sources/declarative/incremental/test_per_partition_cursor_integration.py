#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
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
        "state": {},
        "use_global_cursor": False,
        "states": [
            {
                "partition": {"partition_field": "1"},
                "cursor": {CURSOR_FIELD: "2022-01-15"},
            }
        ],
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


def test_partition_limitation(caplog):
    """
    Test that when the number of partitions exceeds the maximum allowed limit in PerPartitionCursor,
    the oldest partitions are dropped, and the state is updated accordingly.

    In this test, we set the maximum number of partitions to 2 and provide 3 partitions.
    We verify that the state only retains information for the two most recent partitions.
    """
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

    # Use caplog to capture logs
    with caplog.at_level(logging.WARNING, logger="airbyte"):
        with patch.object(SimpleRetriever, "_read_pages", side_effect=records_list):
            with patch.object(PerPartitionCursor, "DEFAULT_MAX_PARTITIONS_NUMBER", 2):
                output = list(source.read(logger, {}, catalog, initial_state))

    # Check if the warning was logged
    logged_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]
    warning_message = (
        'The maximum number of partitions has been reached. Dropping the oldest partition: {"partition_field":"1"}. Over limit: 1.'
    )
    assert warning_message in logged_messages

    final_state = [orjson.loads(orjson.dumps(message.state.stream.stream_state)) for message in output if message.state]
    assert final_state[-1] == {
        "lookback_window": 1,
        "state": {"cursor_field": "2022-02-17"},
        "use_global_cursor": False,
        "states": [
            {
                "partition": {"partition_field": "2"},
                "cursor": {CURSOR_FIELD: "2022-01-16"},
            },
            {
                "partition": {"partition_field": "3"},
                "cursor": {CURSOR_FIELD: "2022-02-17"},
            },
        ],
    }


def test_perpartition_with_fallback(caplog):
    """
    Test that when the number of partitions exceeds the limit in PerPartitionCursor,
    the cursor falls back to using the global cursor for state management.

    This test also checks that the appropriate warning logs are emitted when the partition limit is exceeded.
    """
    source = ManifestDeclarativeSource(
        source_config=ManifestBuilder()
        .with_list_partition_router("Rates", "partition_field", ["1", "2", "3", "4", "5", "6"])
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

    partition_slices = [StreamSlice(partition={"partition_field": str(i)}, cursor_slice={}) for i in range(1, 7)]

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
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-01-17"}, partition_slices[3])],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-02-19"}, partition_slices[3])],
        [],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-02-18"}, partition_slices[4])],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-01-13"}, partition_slices[3])],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-02-18"}, partition_slices[3])],
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
                stream_descriptor=StreamDescriptor(name="Rates", namespace=None),
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

    # Use caplog to capture logs
    with caplog.at_level(logging.WARNING, logger="airbyte"):
        with patch.object(SimpleRetriever, "_read_pages", side_effect=records_list):
            with patch.object(PerPartitionCursor, "DEFAULT_MAX_PARTITIONS_NUMBER", 2):
                output = list(source.read(logger, {}, catalog, initial_state))

    # Check if the warnings were logged
    expected_warning_messages = [
        'The maximum number of partitions has been reached. Dropping the oldest partition: {"partition_field":"1"}. Over limit: 1.',
        'The maximum number of partitions has been reached. Dropping the oldest partition: {"partition_field":"2"}. Over limit: 2.',
        'The maximum number of partitions has been reached. Dropping the oldest partition: {"partition_field":"3"}. Over limit: 3.',
    ]

    logged_messages = [record.message for record in caplog.records if record.levelname == "WARNING"]

    for expected_message in expected_warning_messages:
        assert expected_message in logged_messages

    # Proceed with existing assertions
    final_state = [orjson.loads(orjson.dumps(message.state.stream.stream_state)) for message in output if message.state]
    assert final_state[-1] == {"use_global_cursor": True, "state": {"cursor_field": "2022-02-19"}, "lookback_window": 1}


def test_per_partition_cursor_within_limit(caplog):
    """
    Test that the PerPartitionCursor correctly updates the state for each partition
    when the number of partitions is within the allowed limit.

    This test also checks that no warning logs are emitted when the partition limit is not exceeded.
    """
    source = ManifestDeclarativeSource(
        source_config=ManifestBuilder()
        .with_list_partition_router("Rates", "partition_field", ["1", "2", "3"])
        .with_incremental_sync(
            "Rates",
            start_datetime="2022-01-01",
            end_datetime="2022-03-31",
            datetime_format="%Y-%m-%d",
            cursor_field=CURSOR_FIELD,
            step="P1M",
            cursor_granularity="P1D",
        )
        .build()
    )

    partition_slices = [StreamSlice(partition={"partition_field": str(i)}, cursor_slice={}) for i in range(1, 4)]

    records_list = [
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-01-15"}, partition_slices[0])],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-02-20"}, partition_slices[0])],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-03-25"}, partition_slices[0])],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-01-16"}, partition_slices[1])],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-02-18"}, partition_slices[1])],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-03-28"}, partition_slices[1])],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-01-17"}, partition_slices[2])],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-02-19"}, partition_slices[2])],
        [Record({"a record key": "a record value", CURSOR_FIELD: "2022-03-29"}, partition_slices[2])],
    ]

    configured_stream = ConfiguredAirbyteStream(
        stream=AirbyteStream(name="Rates", json_schema={}, supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental]),
        sync_mode=SyncMode.incremental,
        destination_sync_mode=DestinationSyncMode.append,
    )
    catalog = ConfiguredAirbyteCatalog(streams=[configured_stream])

    initial_state = {}
    logger = MagicMock()

    # Use caplog to capture logs
    with caplog.at_level(logging.WARNING, logger="airbyte"):
        with patch.object(SimpleRetriever, "_read_pages", side_effect=records_list):
            with patch.object(PerPartitionCursor, "DEFAULT_MAX_PARTITIONS_NUMBER", 5):
                output = list(source.read(logger, {}, catalog, initial_state))

    # Since the partition limit is not exceeded, we expect no warnings
    logged_warnings = [record.message for record in caplog.records if record.levelname == "WARNING"]
    assert len(logged_warnings) == 0

    # Proceed with existing assertions
    final_state = [orjson.loads(orjson.dumps(message.state.stream.stream_state)) for message in output if message.state]
    assert final_state[-1] == {
        "lookback_window": 1,
        "state": {"cursor_field": "2022-03-29"},
        "use_global_cursor": False,
        "states": [
            {
                "partition": {"partition_field": "1"},
                "cursor": {CURSOR_FIELD: "2022-03-25"},
            },
            {
                "partition": {"partition_field": "2"},
                "cursor": {CURSOR_FIELD: "2022-03-28"},
            },
            {
                "partition": {"partition_field": "3"},
                "cursor": {CURSOR_FIELD: "2022-03-29"},
            },
        ],
    }
