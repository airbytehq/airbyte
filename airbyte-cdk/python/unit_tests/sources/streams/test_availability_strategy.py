#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.core import StreamData

logger = logging.getLogger("airbyte")


class MockStream(Stream):
    def __init__(self, name: str) -> Stream:
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def primary_key(self) -> Optional[Union[str, List[str], List[List[str]]]]:
        pass

    def read_records(
        self,
        sync_mode: SyncMode,
        cursor_field: List[str] = None,
        stream_slice: Mapping[str, Any] = None,
        stream_state: Mapping[str, Any] = None,
    ) -> Iterable[StreamData]:
        pass


def test_no_availability_strategy():
    stream_1 = MockStream("stream")
    assert stream_1.availability_strategy is None

    stream_1_is_available, _ = stream_1.check_availability(logger)
    assert stream_1_is_available


def test_availability_strategy():
    class MockAvailabilityStrategy(AvailabilityStrategy):
        def check_availability(self, stream: Stream, logger: logging.Logger, source: Optional[Source]) -> Tuple[bool, any]:
            if stream.name == "available_stream":
                return True, None
            return False, f"Could not reach stream '{stream.name}'."

    class MockStreamWithAvailabilityStrategy(MockStream):
        @property
        def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
            return MockAvailabilityStrategy()

    stream_1 = MockStreamWithAvailabilityStrategy("available_stream")
    stream_2 = MockStreamWithAvailabilityStrategy("unavailable_stream")

    for stream in [stream_1, stream_2]:
        assert isinstance(stream.availability_strategy, MockAvailabilityStrategy)

    stream_1_is_available, _ = stream_1.check_availability(logger)
    assert stream_1_is_available

    stream_2_is_available, reason = stream_2.check_availability(logger)
    assert not stream_2_is_available
    assert "Could not reach stream 'unavailable_stream'" in reason
