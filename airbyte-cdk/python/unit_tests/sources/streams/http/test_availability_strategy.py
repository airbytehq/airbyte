#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, List, Mapping, Optional, Tuple

import pytest
import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
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

    # TODO (Ella): Remove explicit definition when turning on default
    @property
    def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
        return HttpAvailabilityStrategy()


@pytest.mark.parametrize(
    ("status_code", "json_contents", "expected_is_available", "expected_messages"),
    [
        (403, {"error": "Something went wrong"}, False, [
            "This is most likely due to insufficient permissions on the credentials in use.",
            "Something went wrong",
        ]),
        (200, {}, True, [])
    ]
)
@pytest.mark.parametrize(
    ("include_source", "expected_docs_url_messages"), [
        (True, ["Please visit https://docs.airbyte.com/integrations/sources/MockSource to learn more."]),
        (False, ["Please visit the connector's documentation to learn more."]),
    ]
)
def test_default_http_availability_strategy(mocker, status_code, json_contents, expected_is_available, expected_messages, include_source, expected_docs_url_messages):
    http_stream = MockHttpStream()
    assert isinstance(http_stream.availability_strategy, HttpAvailabilityStrategy)

    class MockResponseWithJsonContents(requests.Response, mocker.MagicMock):
        def __init__(self, *args, **kvargs):
            mocker.MagicMock.__init__(self)
            requests.Response.__init__(self, **kvargs)
            self.json = mocker.MagicMock()

    class MockSource(AbstractSource):
        def __init__(self, streams: List[Stream] = None):
            self._streams = streams

        def check_connection(self, logger: logging.Logger, config: Mapping[str, Any]) -> Tuple[bool, Optional[Any]]:
            return True, ""

        def streams(self, config: Mapping[str, Any]) -> List[Stream]:
            if not self._streams:
                raise Exception("Stream is not set")
            return self._streams

    response = MockResponseWithJsonContents()
    response.status_code = status_code
    response.json.return_value = json_contents
    mocker.patch.object(requests.Session, "send", return_value=response)

    if include_source:
        source = MockSource(streams=[http_stream])
        actual_is_available, reason = http_stream.check_availability(logger, source)
    else:
        actual_is_available, reason = http_stream.check_availability(logger)

    assert expected_is_available == actual_is_available
    if expected_is_available:
        assert reason is None
    else:
        all_expected_messages = expected_messages + expected_docs_url_messages
        for message in all_expected_messages:
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

    class MockEmptyHttpStream(mocker.MagicMock, MockHttpStream):
        def __init__(self, *args, **kvargs):
            mocker.MagicMock.__init__(self)
            self.read_records = mocker.MagicMock()

    empty_stream = MockEmptyHttpStream()
    assert isinstance(empty_stream, HttpStream)

    assert isinstance(empty_stream.availability_strategy, HttpAvailabilityStrategy)

    # Generator should have no values to generate
    empty_stream.read_records.return_value = iter([])

    logger = logging.getLogger("airbyte.test-source")
    stream_is_available, _ = empty_stream.check_availability(logger)

    assert stream_is_available
    assert empty_stream.read_records.called
