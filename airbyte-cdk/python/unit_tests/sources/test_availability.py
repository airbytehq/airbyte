#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Union

import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource, Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy, ScopedAvailabilityStrategy
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
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
        def get_granted_scopes(self) -> List[str]:
            return ["repo"]

        def required_scopes(self) -> Dict[str, List[str]]:
            return {"repos": ["repo"], "projectV2": ["read:project"]}

    class MockStreamWithScopedAvailabilityStrategy(MockStream):
        @property
        def availability_strategy(self) -> Optional[AvailabilityStrategy]:
            return MockScopedAvailabilityStrategy()

    stream_1 = MockStreamWithScopedAvailabilityStrategy("repos")
    stream_2 = MockStreamWithScopedAvailabilityStrategy("projectV2")

    stream_1_is_available, _ = stream_1.check_availability(logger)
    assert stream_1_is_available is True

    stream_2_is_available, reason = stream_2.check_availability(logger)
    assert stream_2_is_available is False
    assert "Missing required scopes: ['read:project']" in reason


def test_http_availability_strategy(mocker):
    stream = MockHttpStream()
    assert isinstance(stream.availability_strategy, HttpAvailabilityStrategy)

    req = requests.Response()
    req.status_code = 403
    mocker.patch.object(requests.Session, "send", return_value=req)

    is_available, reason = stream.check_availability(logger)
    assert is_available is False

    expected_messages = [
        "This is most likely due to insufficient permissions on the credentials in use.",
        "Please visit the connector's documentation to learn more."
    ]
    for message in expected_messages:
        assert message in reason

    req.status_code = 200
    mocker.patch.object(requests.Session, "send", return_value=req)
    assert stream.check_availability(logger)[0] is True


def test_http_availability_connector_specific_docs(mocker):
    stream = MockHttpStream()
    source = MockSource(streams=[stream])
    assert isinstance(stream.availability_strategy, HttpAvailabilityStrategy)

    req = requests.Response()
    req.status_code = 403
    mocker.patch.object(requests.Session, "send", return_value=req)

    is_available, reason = stream.check_availability(logger, source)
    assert is_available is False

    expected_messages = [
        f"The endpoint to access stream '{stream.name}' returned 403: Forbidden.",
        "This is most likely due to insufficient permissions on the credentials in use.",
        "Please visit https://docs.airbyte.com/integrations/sources/test to learn more."
    ]
    for message in expected_messages:
        assert message in reason
