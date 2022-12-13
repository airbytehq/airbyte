#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, List, Mapping, Optional, Tuple

import pytest
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from airbyte_cdk.sources.streams.http.http import HttpStream
from requests import HTTPError

logger = logging.getLogger("airbyte")


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


def test_default_http_availability_strategy(mocker):
    http_stream = MockHttpStream()
    assert isinstance(http_stream.availability_strategy, HttpAvailabilityStrategy)

    class MockResponse(requests.Response, mocker.MagicMock):
        def __init__(self, *args, **kvargs):
            mocker.MagicMock.__init__(self)
            requests.Response.__init__(self, **kvargs)
            self.json = mocker.MagicMock()

    response = MockResponse()
    response.status_code = 403
    response.json.return_value = {"error": "Oh no!"}
    mocker.patch.object(requests.Session, "send", return_value=response)

    stream_is_available, reason = http_stream.check_availability(logger)
    assert not stream_is_available

    expected_messages = [
        "This is most likely due to insufficient permissions on the credentials in use.",
        "Please visit the connector's documentation to learn more.",
        "Oh no!",
    ]
    for message in expected_messages:
        assert message in reason

    req = requests.Response()
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
    mocker.patch.object(requests.Session, "send", return_value=req, json={"error": "Oh no!"})

    stream_is_available, reason = http_stream.check_availability(logger, source)
    assert not stream_is_available

    expected_messages = [
        f"The endpoint to access stream '{http_stream.name}' returned 403: Forbidden.",
        "This is most likely due to insufficient permissions on the credentials in use.",
        f"Please visit https://docs.airbyte.com/integrations/sources/{source.name} to learn more.",
        # "Oh no!",
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


def test_http_availability_strategy_on_empty_stream(mocker):
    mocker.patch.multiple(HttpStream, __abstractmethods__=set())
    mocker.patch.multiple(Stream, __abstractmethods__=set())

    class MockEmptyStream(mocker.MagicMock, HttpStream):
        page_size = None
        get_json_schema = mocker.MagicMock()

        def __init__(self, *args, **kvargs):
            mocker.MagicMock.__init__(self)
            self.read_records = mocker.MagicMock()

    empty_stream = MockEmptyStream()
    assert isinstance(empty_stream, HttpStream)

    assert isinstance(empty_stream.availability_strategy, HttpAvailabilityStrategy)

    # Generator should have no values to generate
    empty_stream.read_records.return_value = iter([])

    logger = logging.getLogger("airbyte.test-source")
    stream_is_available, _ = empty_stream.check_availability(logger)

    assert stream_is_available
    assert empty_stream.read_records.called
