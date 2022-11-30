#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
import requests
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from airbyte_cdk.models import (
    AirbyteStream,
    SyncMode,
)
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.availability_strategy import (
    AvailabilityStrategy,
    HTTPAvailabilityStrategy,
    ScopedAvailabilityStrategy,
)
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.http import HttpStream

logger = logging.getLogger("airbyte")


class MockSource(AbstractSource):
    def __init__(
        self,
        streams: List[Stream] = None,
    ):
        self._streams = streams

    def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
        return True, ""

    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        if not self._streams:
            raise Exception("Stream is not set")
        return self._streams


def test_availability_strategy():
    class MockAvailabilityStrategy(AvailabilityStrategy):
        def check_availability(self, stream: Stream) -> Tuple[bool, any]:
            if stream.name == "available_stream":
                return True, None
            return False, f"Could not reach stream '{stream.name}'."

    class MockSourceWithAvailabilityStrategy(MockSource):
        @property
        def availability_strategy(self):
            return MockAvailabilityStrategy()

    stream_1 = AirbyteStream(name="available_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])
    stream_2 = AirbyteStream(name="unavailable_stream", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])

    source = MockSourceWithAvailabilityStrategy(streams=[stream_1, stream_2])
    assert isinstance(source.availability_strategy, MockAvailabilityStrategy)
    assert source.availability_strategy.check_availability(stream_1)[0] is True
    assert source.availability_strategy.check_availability(stream_2)[0] is False
    assert "Could not reach stream 'unavailable_stream'" in source.availability_strategy.check_availability(stream_2)[1]


def test_scoped_availability_strategy():
    class MockScopedAvailabilityStrategy(ScopedAvailabilityStrategy):
        def get_granted_scopes(self) -> List[str]:
            return ["repo"]

        def required_scopes(self) -> Dict[str, List[str]]:
            return {"repos": ["repo"], "projectV2": ["read:project"]}

    class MockSourceWithScopedAvailabilityStrategy(MockSource):
        @property
        def availability_strategy(self) -> Optional[AvailabilityStrategy]:
            return MockScopedAvailabilityStrategy()

    stream_1 = AirbyteStream(name="repos", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])
    stream_2 = AirbyteStream(name="projectV2", json_schema={}, supported_sync_modes=[SyncMode.full_refresh])

    source = MockSourceWithScopedAvailabilityStrategy(streams=[stream_1, stream_2])
    assert source.availability_strategy.check_availability(stream_1)[0] is True
    assert source.availability_strategy.check_availability(stream_2)[0] is False
    assert "Missing required scopes: ['read:project']" in source.availability_strategy.check_availability(stream_2)[1]


def test_http_availability_strategy(mocker):
    class StubBasicReadHttpStream(HttpStream):
        url_base = "https://test_base_url.com"
        primary_key = ""

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.resp_counter = 1

        def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
            return None

        def path(self, **kwargs) -> str:
            return ""

        def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
            stub_resp = {"data": self.resp_counter}
            self.resp_counter += 1
            yield stub_resp

    class MockSourceWithHTTPAvailabilityStrategy(MockSource):
        @property
        def availability_strategy(self) -> Optional[AvailabilityStrategy]:
            return HTTPAvailabilityStrategy()

    stream_1 = StubBasicReadHttpStream()
    source = MockSourceWithHTTPAvailabilityStrategy(streams=[stream_1])

    req = requests.Response()
    req.status_code = 403
    mocker.patch.object(requests.Session, "send", return_value=req)
    assert source.availability_strategy.check_availability(stream_1)[0] is False
    assert "403 Client Error" in source.availability_strategy.check_availability(stream_1)[1]

    req.status_code = 200
    mocker.patch.object(requests.Session, "send", return_value=req)
    assert source.availability_strategy.check_availability(stream_1)[0] is True
