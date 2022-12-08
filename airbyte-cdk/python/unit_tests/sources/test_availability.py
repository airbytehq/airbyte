#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource, Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy, ScopedAvailabilityStrategy
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from airbyte_cdk.sources.streams.http.http import HttpStream

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


class MockHttpStream(HttpStream):
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
    pass


def test_no_availability_strategy():
    stream_1 = MockStream("stream")
    assert stream_1.availability_strategy is None

    stream_1_is_available, _ = stream_1.check_availability(logger)
    assert stream_1_is_available is True


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
    assert stream_1_is_available is True

    stream_2_is_available, reason = stream_2.check_availability(logger)
    assert stream_2_is_available is False
    assert "Could not reach stream 'unavailable_stream'" in reason


def test_scoped_availability_strategy():
    class MockScopedAvailabilityStrategy(ScopedAvailabilityStrategy):
        def __init__(self, granted_scopes, required_scopes):
            self._granted_scopes = granted_scopes
            self._required_scopes = required_scopes

        def get_granted_scopes(self, stream: Stream, logger: logging.Logger, source: Optional["Source"]) -> List[str]:
            return self._granted_scopes

        def required_scopes(self, stream: Stream, logger: logging.Logger, source: Optional["Source"]) -> List[str]:
            return self._required_scopes

    class MockStreamWithScopedAvailabilityStrategy(MockStream):
        def __init__(self, availability_strategy, **kwargs):
            self._availability_strategy = availability_strategy
            super().__init__(**kwargs)

        @property
        def availability_strategy(self) -> Optional[AvailabilityStrategy]:
            return self._availability_strategy

    availability_strategy_1 = MockScopedAvailabilityStrategy(
        granted_scopes=["repo"],
        required_scopes=["repo"],
    )
    availability_strategy_2 = MockScopedAvailabilityStrategy(
        granted_scopes=["repo"],
        required_scopes=["read:project"],
    )

    stream_1 = MockStreamWithScopedAvailabilityStrategy(name="repos", availability_strategy=availability_strategy_1)
    stream_2 = MockStreamWithScopedAvailabilityStrategy(name="projectV2", availability_strategy=availability_strategy_2)

    stream_1_is_available, _ = stream_1.check_availability(logger)
    assert stream_1_is_available is True

    stream_2_is_available, reason = stream_2.check_availability(logger)
    assert stream_2_is_available is False
    assert "Missing required scopes: ['read:project']" in reason


def test_default_http_availability_strategy(mocker):
    http_stream = MockHttpStream()
    assert isinstance(http_stream.availability_strategy, HttpAvailabilityStrategy)

    req = requests.Response()
    req.status_code = 403
    mocker.patch.object(requests.Session, "send", return_value=req)

    stream_is_available, reason = http_stream.check_availability(logger)
    assert stream_is_available is False

    expected_messages = [
        "This is most likely due to insufficient permissions on the credentials in use.",
        "Please visit the connector's documentation to learn more."
    ]
    for message in expected_messages:
        assert message in reason

    req.status_code = 200
    mocker.patch.object(requests.Session, "send", return_value=req)

    stream_is_available, _ = http_stream.check_availability(logger)
    assert stream_is_available is True


def test_http_availability_connector_specific_docs(mocker):
    class MockSource(AbstractSource):
        def __init__(self, streams: List[Stream] = None):
            self._streams = streams

        def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
            return True, ""

        def streams(self, config: Mapping[str, Any]) -> List[Stream]:
            if not self._streams:
                raise Exception("Stream is not set")
            return self._streams

    http_stream = MockHttpStream()
    source = MockSource(streams=[http_stream])
    assert isinstance(http_stream.availability_strategy, HttpAvailabilityStrategy)

    req = requests.Response()
    req.status_code = 403
    mocker.patch.object(requests.Session, "send", return_value=req)

    stream_is_available, reason = http_stream.check_availability(logger, source)
    assert stream_is_available is False

    expected_messages = [
        f"The endpoint to access stream '{http_stream.name}' returned 403: Forbidden.",
        "This is most likely due to insufficient permissions on the credentials in use.",
        f"Please visit https://docs.airbyte.com/integrations/sources/{source.name} to learn more."
    ]
    for message in expected_messages:
        assert message in reason
