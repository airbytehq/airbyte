#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
from source_openweather.streams import OneCall


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(OneCall, "__abstractmethods__", set())


@pytest.mark.parametrize(
    ("stream", "expected_params"),
    [
        (OneCall(appid="test_appid", lat=1.0, lon=1.0), {"appid": "test_appid", "lat": 1.0, "lon": 1.0}),
        (
            OneCall(appid="test_appid", lat=1.0, lon=1.0, lang=None, units=None),
            {"appid": "test_appid", "lat": 1.0, "lon": 1.0},
        ),
        (
            OneCall(appid="test_appid", lat=1.0, lon=1.0, lang="fr", units="metric"),
            {"appid": "test_appid", "lat": 1.0, "lon": 1.0, "lang": "fr", "units": "metric"},
        ),
    ],
)
def test_request_params(stream, expected_params):
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    assert stream.request_params(**inputs) == expected_params


@pytest.mark.parametrize(
    ("response_data", "stream_state", "expect_record"),
    [
        ({"current": {"dt": 1}}, {}, True),
        ({"current": {"dt": 2}}, {"dt": 1}, True),
        ({"current": {"dt": 1}}, {"dt": 2}, False),
    ],
)
def test_parse_response(patch_base_class, response_data, stream_state, expect_record):
    stream = OneCall(appid="test_appid", lat=1.0, lon=1.0)
    response_mock = MagicMock()
    response_mock.json.return_value = response_data
    if expect_record:
        assert stream.parse_response(response=response_mock, stream_state=stream_state) == [response_mock.json.return_value]
    else:
        assert stream.parse_response(response=response_mock, stream_state=stream_state) == []


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, False),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = OneCall(appid="test_appid", lat=1.0, lon=1.0)
    assert stream.should_retry(response_mock) == should_retry
