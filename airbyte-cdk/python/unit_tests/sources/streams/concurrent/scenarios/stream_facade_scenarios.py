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
    def __init__(
        self,
        slice_key,
        slice_values_to_records_or_exception: Mapping[Optional[str], List[Union[Mapping[str, Any], Exception]]],
        name,
        json_schema,
        primary_key=None,
    ):
        self._slice_key = slice_key
        self._slice_values_to_records = slice_values_to_records_or_exception
        self._name = name
        self._json_schema = json_schema
        self._primary_key = primary_key

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: Optional[List[str]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        stream_state: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[StreamData]:
        for record_or_exception in self._get_record_or_exception_iterable(stream_slice):
            if isinstance(record_or_exception, Exception):
                raise record_or_exception
            else:
                yield record_or_exception

    def _get_record_or_exception_iterable(
        self, stream_slice: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Union[Mapping[str, Any], Exception]]:
        if stream_slice is None:
            return self._slice_values_to_records[None]
        else:
            return self._slice_values_to_records[stream_slice[self._slice_key]]

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return self._primary_key

    @property
    def name(self) -> str:
        return self._name

    def get_json_schema(self) -> Mapping[str, Any]:
        return self._json_schema

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        if self._slice_key:
            for slice_value in self._slice_values_to_records.keys():
                yield {self._slice_key: slice_value}
        else:
            yield None


_stream1 = _MockStream(
    None,
    {None: [{"id": "1"}, {"id": "2"}]},
    "stream1",
    json_schema={
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
        },
    },
)

_stream_raising_exception = _MockStream(
    None,
    {None: [{"id": "1"}, ValueError("test exception")]},
    "stream1",
    json_schema={
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
        },
    },
)

_stream_with_primary_key = _MockStream(
    None,
    {None: [{"id": "1"}, {"id": "2"}]},
    "stream1",
    json_schema={
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
        },
    },
    primary_key="id",
)

_stream2 = _MockStream(
    None,
    {None: [{"id": "A"}, {"id": "B"}]},
    "stream2",
    json_schema={
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
        },
    },
)

_stream_with_single_slice = _MockStream(
    "slice_key",
    {"s1": [{"id": "1"}, {"id": "2"}]},
    "stream1",
    json_schema={
        "type": "object",
        "properties": {
            "id": {"type": ["null", "string"]},
        },
    },
)

_stream_with_multiple_slices = _MockStream(
    "slice_key",
    {
        "s1": [{"id": "1"}, {"id": "2"}],
        "s2": [{"id": "3"}, {"id": "4"}],
    },
    "stream1",
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
    .set_expected_logs(
        {
            "read": [
                {"level": "INFO", "message": "Starting syncing StreamFacadeSource"},
                {"level": "INFO", "message": "Marking stream stream1 as STARTED"},
                {"level": "INFO", "message": "Syncing stream: stream1"},
                {"level": "INFO", "message": "Marking stream stream1 as RUNNING"},
                {"level": "INFO", "message": "Read 2 records from stream1 stream"},
                {"level": "INFO", "message": "Marking stream stream1 as STOPPED"},
                {"level": "INFO", "message": "Finished syncing stream1"},
                {"level": "INFO", "message": "StreamFacadeSource runtimes"},
                {"level": "INFO", "message": "Finished syncing StreamFacadeSource"},
            ]
        }
    )
    .set_log_levels({"ERROR", "WARN", "WARNING", "INFO", "DEBUG"})
    .build()
)

test_stream_facade_raises_exception = (
    TestScenarioBuilder()
    .set_name("test_stream_facade_raises_exception")
    .set_config({})
    .set_source_builder(StreamFacadeSourceBuilder().set_streams([_stream_raising_exception]))
    .set_expected_records(
        [
            {"data": {"id": "1"}, "stream": "stream1"},
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
    .set_expected_read_error(ValueError, "test exception")
    .build()
)

test_stream_facade_single_stream_with_primary_key = (
    TestScenarioBuilder()
    .set_name("test_stream_facade_stream_with_primary_key")
    .set_config({})
    .set_source_builder(StreamFacadeSourceBuilder().set_streams([_stream1]))
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

test_stream_facade_single_stream_with_single_slice = (
    TestScenarioBuilder()
    .set_name("test_stream_facade_single_stream_with_single_slice")
    .set_config({})
    .set_source_builder(StreamFacadeSourceBuilder().set_streams([_stream1]))
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

test_stream_facade_single_stream_with_multiple_slices = (
    TestScenarioBuilder()
    .set_name("test_stream_facade_single_stream_with_multiple_slice")
    .set_config({})
    .set_source_builder(StreamFacadeSourceBuilder().set_streams([_stream_with_multiple_slices]))
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

test_stream_facade_single_stream_with_multiple_slices_with_concurrency_level_two = (
    TestScenarioBuilder()
    .set_name("test_stream_facade_single_stream_with_multiple_slice_with_concurrency_level_two")
    .set_config({})
    .set_source_builder(StreamFacadeSourceBuilder().set_streams([_stream_with_multiple_slices]))
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
