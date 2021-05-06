from typing import Mapping, Any, List, Tuple, Optional, Callable

import pytest

from airbyte_cdk import AirbyteConnectionStatus, Status
from airbyte_cdk.base_python import AbstractSource, Stream, AirbyteLogger


class MockSource(AbstractSource):
    def __init__(self, check_lambda: Callable[[], Tuple[bool, Optional[Any]]] = None, streams: List[Stream] = None):
        self.streams = streams
        self.check_lambda = check_lambda

    def check_connection(self, logger: AirbyteLogger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        return self.check_lambda()

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return self.streams


@pytest.fixture
def logger() -> AirbyteLogger:
    return AirbyteLogger()


def test_successful_check():
    expected = AirbyteConnectionStatus(status=Status.SUCCEEDED)
    assert expected == MockSource(check_lambda=lambda: (True, None)).check(logger, {})

def test_failed_check():
    pass


def test_raising_check():
    pass


def test_discover():
    pass


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
