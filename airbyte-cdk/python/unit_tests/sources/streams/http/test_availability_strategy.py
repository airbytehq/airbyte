#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import io
import json
import logging
from typing import Any, Iterable, Mapping, Optional

import pytest
import requests
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy
from airbyte_cdk.sources.streams.http.http import HttpStream

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


@pytest.mark.parametrize(
    ("status_code", "json_contents", "expected_is_available", "expected_messages"),
    [
        (
            403,
            {"error": "Something went wrong"},
            False,
            [
                "Forbidden. You don't have permission to access this resource.",
                "Forbidden. You don't have permission to access this resource.",
            ],
        ),
        (200, {}, True, []),
    ],
)
@pytest.mark.parametrize(
    ("include_source", "expected_docs_url_messages"),
    [
        (True, ["Forbidden. You don't have permission to access this resource."]),
        (False, ["Forbidden. You don't have permission to access this resource."]),
    ],
)
@pytest.mark.parametrize("records_as_list", [True, False])
def test_default_http_availability_strategy(
    mocker,
    status_code,
    json_contents,
    expected_is_available,
    expected_messages,
    include_source,
    expected_docs_url_messages,
    records_as_list,
):
    class MockListHttpStream(MockHttpStream):
        def read_records(self, *args, **kvargs):
            if records_as_list:
                return list(super().read_records(*args, **kvargs))
            else:
                return super().read_records(*args, **kvargs)

    http_stream = MockListHttpStream()
    response = requests.Response()
    response.status_code = status_code
    response.raw = io.BytesIO(json.dumps(json_contents).encode("utf-8"))
    mocker.patch.object(requests.Session, "send", return_value=response)

    actual_is_available, reason = HttpAvailabilityStrategy().check_availability(http_stream, logger)

    assert actual_is_available == expected_is_available
    if expected_is_available:
        assert reason is None
    else:
        all_expected_messages = expected_messages + expected_docs_url_messages
        for message in all_expected_messages:
            assert message in reason


def test_http_availability_raises_unhandled_error(mocker):
    http_stream = MockHttpStream()

    req = requests.Response()
    req.status_code = 404
    mocker.patch.object(requests.Session, "send", return_value=req)

    assert (False, "Not found. The requested resource was not found on the server.") == HttpAvailabilityStrategy().check_availability(
        http_stream, logger
    )


def test_send_handles_retries_when_checking_availability(mocker, caplog):
    mocker.patch("time.sleep", lambda x: None)
    http_stream = MockHttpStream()

    req_1 = requests.Response()
    req_1.status_code = 429
    req_2 = requests.Response()
    req_2.status_code = 503
    req_3 = requests.Response()
    req_3.status_code = 200
    mock_send = mocker.patch.object(requests.Session, "send", side_effect=[req_1, req_2, req_3])

    with caplog.at_level(logging.INFO):
        stream_is_available, _ = HttpAvailabilityStrategy().check_availability(stream=http_stream, logger=logger)

    assert stream_is_available
    assert mock_send.call_count == 3
    for message in ["Caught retryable error", "Service unavailable", "Service unavailable"]:
        assert message in caplog.text


@pytest.mark.parametrize("records_as_list", [True, False])
def test_http_availability_strategy_on_empty_stream(mocker, records_as_list):
    class MockEmptyHttpStream(mocker.MagicMock, MockHttpStream):
        def __init__(self, *args, **kvargs):
            mocker.MagicMock.__init__(self)
            self.read_records = mocker.MagicMock()

    empty_stream = MockEmptyHttpStream()
    assert isinstance(empty_stream, HttpStream)

    # Generator should have no values to generate
    if records_as_list:
        empty_stream.read_records.return_value = []
    else:
        empty_stream.read_records.return_value = iter([])

    logger = logging.getLogger("airbyte.test-source")
    stream_is_available, _ = HttpAvailabilityStrategy().check_availability(stream=empty_stream, logger=logger)

    assert stream_is_available
    assert empty_stream.read_records.called
