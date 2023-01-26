#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

import logging
from typing import Any, Iterable, Mapping, Optional
from unittest.mock import MagicMock

import pytest
import requests
from airbyte_cdk.sources.declarative.checks.check_stream import CheckStream
from airbyte_cdk.sources.streams.availability_strategy import AvailabilityStrategy
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.availability_strategy import HttpAvailabilityStrategy

logger = logging.getLogger("test")
config = dict()

stream_names = ["s1"]
record = MagicMock()


@pytest.mark.parametrize(
    "test_name, record, streams_to_check, stream_slice, expectation",
    [
        ("test_success_check", record, stream_names, {}, (True, None)),
        ("test_success_check_stream_slice", record, stream_names, {"slice": "slice_value"}, (True, None)),
        ("test_fail_check", None, stream_names, {}, (True, None)),
        ("test_try_to_check_invalid stream", record, ["invalid_stream_name"], {}, None),
    ],
)
@pytest.mark.parametrize("slices_as_list", [True, False])
def test_check_stream_with_slices_as_list(test_name, record, streams_to_check, stream_slice, expectation, slices_as_list):
    stream = MagicMock()
    stream.name = "s1"
    stream.availability_strategy = None
    if slices_as_list:
        stream.stream_slices.return_value = [stream_slice]
    else:
        stream.stream_slices.return_value = iter([stream_slice])

    stream.read_records.side_effect = mock_read_records({frozenset(stream_slice): iter([record])})

    source = MagicMock()
    source.streams.return_value = [stream]

    check_stream = CheckStream(streams_to_check, options={})

    if expectation:
        actual = check_stream.check_connection(source, logger, config)
        assert actual == expectation
    else:
        with pytest.raises(ValueError):
            check_stream.check_connection(source, logger, config)


def mock_read_records(responses, default_response=None, **kwargs):
    return lambda stream_slice, sync_mode: responses[frozenset(stream_slice)] if frozenset(stream_slice) in responses else default_response


def test_check_empty_stream():
    stream = MagicMock()
    stream.name = "s1"
    stream.availability_strategy = None
    stream.read_records.return_value = iter([])
    stream.stream_slices.return_value = iter([None])

    source = MagicMock()
    source.streams.return_value = [stream]

    check_stream = CheckStream(["s1"], options={})
    stream_is_available, reason = check_stream.check_connection(source, logger, config)
    assert stream_is_available


def test_check_stream_with_no_stream_slices_aborts():
    stream = MagicMock()
    stream.name = "s1"
    stream.availability_strategy = None
    stream.stream_slices.return_value = iter([])

    source = MagicMock()
    source.streams.return_value = [stream]

    check_stream = CheckStream(["s1"], options={})
    stream_is_available, reason = check_stream.check_connection(source, logger, config)
    assert not stream_is_available
    assert "no stream slices were found, likely because the parent stream is empty" in reason


@pytest.mark.parametrize(
    "test_name, response_code, available_expectation, expected_messages",
    [
        ("test_stream_unavailable_unhandled_error", 404, False, ["Unable to connect to stream mock_http_stream", "404 Client Error"]),
        ("test_stream_unavailable_handled_error", 403, False, [
            "The endpoint to access stream 'mock_http_stream' returned 403: Forbidden.",
            "This is most likely due to insufficient permissions on the credentials in use.",
        ]),
        ("test_stream_available", 200, True, []),
    ],
)
def test_check_http_stream_via_availability_strategy(mocker, test_name, response_code, available_expectation, expected_messages):
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

        # TODO (Ella): Remove explicit definition when turning on default
        @property
        def availability_strategy(self) -> Optional["AvailabilityStrategy"]:
            return HttpAvailabilityStrategy()

    http_stream = MockHttpStream()
    assert isinstance(http_stream, HttpStream)
    assert isinstance(http_stream.availability_strategy, HttpAvailabilityStrategy)

    source = MagicMock()
    source.streams.return_value = [http_stream]

    check_stream = CheckStream(stream_names=["mock_http_stream"], options={})

    req = requests.Response()
    req.status_code = response_code
    mocker.patch.object(requests.Session, "send", return_value=req)

    logger = logging.getLogger(f"airbyte.{getattr(source, 'name', '')}")
    stream_is_available, reason = check_stream.check_connection(source, logger, config)

    assert stream_is_available == available_expectation
    for message in expected_messages:
        assert message in reason
