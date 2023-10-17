#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
from typing import Any, Iterable, List, Mapping, Optional, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.core import StreamData
from unit_tests.sources.file_based.scenarios.scenario_builder import TestScenarioBuilder
from unit_tests.sources.streams.concurrent.scenarios.stream_facade_builder import StreamFacadeSourceBuilder


class _MockStream(Stream):
    def __init__(self, records, name, json_schema):
        self._records = records
        self._name = name
        self._json_schema = json_schema

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        # FIXME: test stream slice or something
        yield from self._records

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        # FIXME: probably test this
        return None

    @property
    def name(self) -> str:
        return self._name

    def get_json_schema(self) -> Mapping[str, Any]:
        return self._json_schema


_stream1 = _MockStream(
    [{"id": "1"}, {"id": "2"}],
    "stream1",
    json_schema={
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
        },
    },
)

_stream2 = _MockStream(
    [{"id": "A"}, {"id": "B"}],
    "stream2",
    json_schema={
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
        },
    },
)

test_stream_facade_single_stream = (
    TestScenarioBuilder()
    .set_name("test_stream_facade_single_stream")
    .set_config({})
    .set_source_builder(StreamFacadeSourceBuilder().set_streams([_stream1]))
    .set_expected_records(
        [
            {"data": {"id": "1"}, "stream": "stream1"},
            {"data": {"id": "2"}, "stream": "stream1"},
        ]
    )
    # FIXME: add a test with the logs
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

test_stream_facade_multiple_streams = (
    TestScenarioBuilder()
    .set_name("test_stream_facade_multiple_streams")
    .set_config({})
    .set_source_builder(StreamFacadeSourceBuilder().set_streams([_stream1, _stream2]))
    .set_expected_records(
        [
            {"data": {"id": "1"}, "stream": "stream1"},
            {"data": {"id": "2"}, "stream": "stream1"},
            {"data": {"id": "A"}, "stream": "stream2"},
            {"data": {"id": "B"}, "stream": "stream2"},
        ]
    )
    # FIXME: add a test with the logs
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
