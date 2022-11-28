#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#


from typing import Any, Iterable, List, Mapping
from unittest import mock

import pytest
from airbyte_cdk.models import AirbyteStream, SyncMode
from airbyte_cdk.sources.streams import Stream


class StreamStubFullRefresh(Stream):
    """
    Stub full refresh class to assist with testing.
    """

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        pass

    primary_key = None


def test_as_airbyte_stream_full_refresh(mocker):
    """
    Should return an full refresh AirbyteStream with information matching the
    provided Stream interface.
    """
    test_stream = StreamStubFullRefresh()

    mocker.patch.object(StreamStubFullRefresh, "get_json_schema", return_value={})
    airbyte_stream = test_stream.as_airbyte_stream()

    exp = AirbyteStream(name="stream_stub_full_refresh", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])
    assert exp == airbyte_stream


class StreamStubIncremental(Stream):
    """
    Stub full incremental class to assist with testing.
    """

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        pass

    cursor_field = "test_cursor"
    primary_key = "primary_key"
    namespace = "test_namespace"


class StreamStubIncrementalEmptyNamespace(Stream):
    """
    Stub full incremental class, with empty namespace, to assist with testing.
    """

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        pass

    cursor_field = "test_cursor"
    primary_key = "primary_key"
    namespace = ""


def test_as_airbyte_stream_incremental(mocker):
    """
    Should return an incremental refresh AirbyteStream with information matching
    the provided Stream interface.
    """
    test_stream = StreamStubIncremental()

    mocker.patch.object(StreamStubIncremental, "get_json_schema", return_value={})
    airbyte_stream = test_stream.as_airbyte_stream()

    exp = AirbyteStream(
        name="stream_stub_incremental",
        namespace="test_namespace",
        json_schema={},
        supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        default_cursor_field=["test_cursor"],
        source_defined_cursor=True,
        source_defined_primary_key=[["primary_key"]],
    )
    assert exp == airbyte_stream


def test_supports_incremental_cursor_set():
    """
    Should return true if cursor is set.
    """
    test_stream = StreamStubIncremental()
    test_stream.cursor_field = "test_cursor"

    assert test_stream.supports_incremental


def test_supports_incremental_cursor_not_set():
    """
    Should return false if cursor is not.
    """
    test_stream = StreamStubFullRefresh()

    assert not test_stream.supports_incremental


def test_namespace_set():
    """
    Should allow namespace property to be set.
    """
    test_stream = StreamStubIncremental()

    assert test_stream.namespace == "test_namespace"


def test_namespace_set_to_empty_string(mocker):
    """
    Should not set namespace property if equal to empty string.
    """
    test_stream = StreamStubIncremental()

    mocker.patch.object(StreamStubIncremental, "get_json_schema", return_value={})
    mocker.patch.object(StreamStubIncremental, "namespace", "")

    airbyte_stream = test_stream.as_airbyte_stream()

    exp = AirbyteStream(
        name="stream_stub_incremental",
        json_schema={},
        supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        default_cursor_field=["test_cursor"],
        source_defined_cursor=True,
        source_defined_primary_key=[["primary_key"]],
        namespace=None,
    )
    assert exp == airbyte_stream


def test_namespace_not_set():
    """
    Should be equal to unset value of None.
    """
    test_stream = StreamStubFullRefresh()

    assert test_stream.namespace is None


@pytest.mark.parametrize(
    "test_input, expected",
    [("key", [["key"]]), (["key1", "key2"], [["key1"], ["key2"]]), ([["key1", "key2"], ["key3"]], [["key1", "key2"], ["key3"]])],
)
def test_wrapped_primary_key_various_argument(test_input, expected):
    """
    Should always wrap primary key into list of lists.
    """

    wrapped = Stream._wrapped_primary_key(test_input)

    assert wrapped == expected


@mock.patch("airbyte_cdk.sources.utils.schema_helpers.ResourceSchemaLoader.get_schema")
def test_get_json_schema_is_cached(mocked_method):
    stream = StreamStubFullRefresh()
    for i in range(5):
        stream.get_json_schema()
    assert mocked_method.call_count == 1
