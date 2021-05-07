# MIT License
#
# Copyright (c) 2020 Airbyte
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


from typing import Any, Callable, Iterable, List, Mapping, Optional, Tuple, Union

import pytest
from airbyte_cdk import AirbyteCatalog, AirbyteConnectionStatus, AirbyteStream, Status, SyncMode
from airbyte_cdk.base_python import AbstractSource, AirbyteLogger, Stream


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
    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[Mapping[str, Any]]:
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
    mocker.patch.object(stream1, "as_airbyte_stream", return_value=airbyte_stream1)
    mocker.patch.object(stream2, "as_airbyte_stream", return_value=airbyte_stream2)

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
