#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional
from unittest import mock

import pytest
import requests
from airbyte_cdk.models import AirbyteStream, SyncMode
from airbyte_cdk.sources.streams import CheckpointMixin, Stream
from airbyte_cdk.sources.streams.checkpoint import (
    Cursor,
    CursorBasedCheckpointReader,
    FullRefreshCheckpointReader,
    IncrementalCheckpointReader,
    LegacyCursorBasedCheckpointReader,
    ResumableFullRefreshCheckpointReader,
    ResumableFullRefreshCursor,
)
from airbyte_cdk.sources.streams.http import HttpStream, HttpSubStream
from airbyte_cdk.sources.types import StreamSlice

logger = logging.getLogger("airbyte")


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


class StreamStubIncremental(Stream, CheckpointMixin):
    """
    Stub full incremental class to assist with testing.
    """

    _state = {}

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

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        self._state = value


class StreamStubResumableFullRefresh(Stream, CheckpointMixin):
    """
    Stub full incremental class to assist with testing.
    """

    _state = {}

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        pass

    primary_key = "primary_key"

    @property
    def state(self) -> MutableMapping[str, Any]:
        return self._state

    @state.setter
    def state(self, value: MutableMapping[str, Any]) -> None:
        self._state = value


class StreamStubLegacyStateInterface(Stream):
    """
    Stub full incremental class to assist with testing.
    """

    _state = {}

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

    def get_updated_state(
        self, current_stream_state: MutableMapping[str, Any], latest_record: Mapping[str, Any]
    ) -> MutableMapping[str, Any]:
        return {}


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


class HttpSubStreamStubFullRefreshLegacySlices(HttpSubStream):
    """
    Stub substream full refresh class to assist with testing.
    """

    primary_key = "primary_key"

    @property
    def url_base(self) -> str:
        return "https://airbyte.io/api/v1"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "/stub"

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        return []


class CursorBasedStreamStubFullRefresh(StreamStubFullRefresh):
    def get_cursor(self) -> Optional[Cursor]:
        return ResumableFullRefreshCursor()


class LegacyCursorBasedStreamStubFullRefresh(CursorBasedStreamStubFullRefresh):
    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from [{}]


class MultipleSlicesStreamStub(HttpStream):
    """
    Stub full refresh class that returns multiple StreamSlice instances to assist with testing.
    """

    primary_key = "primary_key"

    @property
    def url_base(self) -> str:
        return "https://airbyte.io/api/v1"

    def stream_slices(
        self, *, sync_mode: SyncMode, cursor_field: Optional[List[str]] = None, stream_state: Optional[Mapping[str, Any]] = None
    ) -> Iterable[Optional[Mapping[str, Any]]]:
        yield from [
            StreamSlice(partition={"parent_id": "korra"}, cursor_slice={}),
            StreamSlice(partition={"parent_id": "asami"}, cursor_slice={}),
        ]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        pass

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "/stub"

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        return []


class ParentHttpStreamStub(HttpStream):
    primary_key = "primary_key"
    url_base = "https://airbyte.io/api/v1"

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
        return [{"id": 400, "name": "a_parent_record"}]

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
        return None

    def path(
        self,
        *,
        stream_state: Optional[Mapping[str, Any]] = None,
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> str:
        return "/parent"

    def parse_response(
        self,
        response: requests.Response,
        *,
        stream_state: Mapping[str, Any],
        stream_slice: Optional[Mapping[str, Any]] = None,
        next_page_token: Optional[Mapping[str, Any]] = None,
    ) -> Iterable[Mapping[str, Any]]:
        return []


def test_as_airbyte_stream_full_refresh(mocker):
    """
    Should return an full refresh AirbyteStream with information matching the
    provided Stream interface.
    """
    test_stream = StreamStubFullRefresh()

    mocker.patch.object(StreamStubFullRefresh, "get_json_schema", return_value={})
    airbyte_stream = test_stream.as_airbyte_stream()

    exp = AirbyteStream(name="stream_stub_full_refresh", json_schema={}, supported_sync_modes=[SyncMode.full_refresh], is_resumable=False)
    assert airbyte_stream == exp


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
        is_resumable=True,
    )
    assert airbyte_stream == exp


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
        is_resumable=True,
    )
    assert airbyte_stream == exp


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


@pytest.mark.parametrize(
    "stream, stream_state, expected_checkpoint_reader_type",
    [
        pytest.param(StreamStubIncremental(), {}, IncrementalCheckpointReader, id="test_incremental_checkpoint_reader"),
        pytest.param(StreamStubFullRefresh(), {}, FullRefreshCheckpointReader, id="test_full_refresh_checkpoint_reader"),
        pytest.param(
            StreamStubResumableFullRefresh(), {}, ResumableFullRefreshCheckpointReader, id="test_resumable_full_refresh_checkpoint_reader"
        ),
        pytest.param(
            StreamStubLegacyStateInterface(), {}, IncrementalCheckpointReader, id="test_incremental_checkpoint_reader_with_legacy_state"
        ),
        pytest.param(
            CursorBasedStreamStubFullRefresh(),
            {"next_page_token": 10},
            CursorBasedCheckpointReader,
            id="test_checkpoint_reader_using_rfr_cursor",
        ),
        pytest.param(
            LegacyCursorBasedStreamStubFullRefresh(),
            {},
            LegacyCursorBasedCheckpointReader,
            id="test_full_refresh_checkpoint_reader_for_legacy_slice_format",
        ),
    ],
)
def test_get_checkpoint_reader(stream: Stream, stream_state, expected_checkpoint_reader_type):
    checkpoint_reader = stream._get_checkpoint_reader(
        logger=logger,
        cursor_field=["updated_at"],
        sync_mode=SyncMode.incremental,
        stream_state=stream_state,
    )

    assert isinstance(checkpoint_reader, expected_checkpoint_reader_type)

    if isinstance(checkpoint_reader, CursorBasedCheckpointReader):
        cursor = checkpoint_reader._cursor
        if isinstance(cursor, ResumableFullRefreshCursor):
            actual_cursor_state = cursor.get_stream_state()

            assert actual_cursor_state == stream_state


def test_checkpoint_reader_with_no_partitions():
    """
    Tests the edge case where an incremental stream might not generate any partitions, but should still attempt at least
    one iteration of calling read_records()
    """
    stream = StreamStubIncremental()
    checkpoint_reader = stream._get_checkpoint_reader(
        logger=logger,
        cursor_field=["updated_at"],
        sync_mode=SyncMode.incremental,
        stream_state={},
    )

    assert checkpoint_reader.next() == {}
