#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, List, Mapping, Optional, Tuple, Union

import pytest
import requests
from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources import AbstractSource, Source
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.core import StreamData
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from airbyte_cdk.sources.streams.http.http import HttpStream
from requests import HTTPError

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

    def retry_factor(self) -> float:
        return 0.01


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


def test_default_http_availability_strategy(mocker):
    http_stream = MockHttpStream()
    assert isinstance(http_stream.availability_strategy, HttpAvailabilityStrategy)

    req = requests.Response()
    req.status_code = 403
    mocker.patch.object(requests.Session, "send", return_value=req)

    stream_is_available, reason = http_stream.check_availability(logger)
    assert not stream_is_available

    expected_messages = [
        "This is most likely due to insufficient permissions on the credentials in use.",
        "Please visit the connector's documentation to learn more."
    ]
    for message in expected_messages:
        assert message in reason

    req.status_code = 200
    mocker.patch.object(requests.Session, "send", return_value=req)

    stream_is_available, _ = http_stream.check_availability(logger)
    assert stream_is_available


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
    assert not stream_is_available

    expected_messages = [
        f"The endpoint to access stream '{http_stream.name}' returned 403: Forbidden.",
        "This is most likely due to insufficient permissions on the credentials in use.",
        f"Please visit https://docs.airbyte.com/integrations/sources/{source.name} to learn more."
    ]
    for message in expected_messages:
        assert message in reason


def test_http_availability_raises_unhandled_error(mocker):
    http_stream = MockHttpStream()
    assert isinstance(http_stream.availability_strategy, HttpAvailabilityStrategy)

    req = requests.Response()
    req.status_code = 404
    mocker.patch.object(requests.Session, "send", return_value=req)

    with pytest.raises(HTTPError):
        http_stream.check_availability(logger)


def test_send_handles_retries_when_checking_availability(mocker, caplog):
    http_stream = MockHttpStream()
    assert isinstance(http_stream.availability_strategy, HttpAvailabilityStrategy)

    req_1 = requests.Response()
    req_1.status_code = 429
    req_2 = requests.Response()
    req_2.status_code = 503
    req_3 = requests.Response()
    req_3.status_code = 200
    mock_send = mocker.patch.object(requests.Session, "send", side_effect=[req_1, req_2, req_3])

    with caplog.at_level(logging.INFO):
        stream_is_available, _ = http_stream.check_availability(logger)

    assert stream_is_available
    assert mock_send.call_count == 3
    for message in ["Caught retryable error", "Response Code: 429", "Response Code: 503"]:
        assert message in caplog.text
