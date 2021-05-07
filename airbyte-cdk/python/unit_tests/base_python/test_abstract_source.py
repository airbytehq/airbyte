from typing import Mapping, Any, List, Tuple, Optional, Callable, Union, Iterable
from unittest.mock import Mock, MagicMock

import pytest

from airbyte_cdk import AirbyteConnectionStatus, Status, SyncMode, AirbyteStream, AirbyteCatalog
from airbyte_cdk.base_python import AbstractSource, Stream, AirbyteLogger


class MockSource(AbstractSource):
    def __init__(self, check_lambda: Callable[[], Tuple[bool, Optional[Any]]] = None, streams: List[Stream] = None):
        self._streams = streams
        self.check_lambda = check_lambda

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        return self.check_lambda()

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return self._streams


@pytest.fixture
def logger() -> AirbyteLogger:
    return AirbyteLogger()


def test_successful_check():
    expected = AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert expected == MockSource(check_lambda=lambda: (True, None)).check(logger, {})


def test_failed_check():
    expected = AirbyteConnectionStatus(status=Status.FAILED, message="womp womp")
    assert expected == MockSource(check_lambda=lambda: (False, "womp womp")).check(logger, {})


def test_raising_check():
    expected = AirbyteConnectionStatus(status=Status.FAILED, message=f"{Exception('this should fail')}")
    assert expected == MockSource(check_lambda=lambda: exec('raise Exception("this should fail")')).check(logger, {})


class MockStream(Stream):

    def read_records(self, sync_mode: SyncMode, cursor_field: List[str] = None, stream_slice: Mapping[str, Any] = None,
                     stream_state: Mapping[str, Any] = None) -> Iterable[Mapping[str, Any]]:
        pass

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        return "pk"


def test_discover(mocker):
    airbyte_stream1 = AirbyteStream(
        name="1",
        json_schema={},
        supported_sync_modes=[SyncMode.full_refresh, SyncMode.incremental],
        default_cursor_field=["cursor"],
        source_defined_cursor=True,
        source_defined_primary_key=[["pk"]],
    )
    airbyte_stream2 = AirbyteStream(name="2", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])

    stream1 = MockStream()
    stream2 = MockStream()
    mocker.patch.object(stream1, 'as_airbyte_stream', return_value=airbyte_stream1)
    mocker.patch.object(stream2, 'as_airbyte_stream', return_value=airbyte_stream2)

    expected = AirbyteCatalog(streams=[airbyte_stream1, airbyte_stream2])
    src = MockSource(check_lambda=lambda: (True, None), streams=[stream1, stream2])

    assert expected == src.discover(logger, {})


def test_read_nonexistent_stream_raises_exception():
    pass


def test_valid_fullrefresh_read_no_slices():
    pass


def test_valid_full_refresh_read_with_slices():
    pass


def test_valid_incremental_read_with_record_interval():
    pass


def test_valid_incremental_read_with_no_interval():
    pass


def test_valid_incremental_read_with_slices():
    pass
