# #
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import datetime
from http import HTTPStatus
from typing import Any, Mapping
from unittest.mock import MagicMock

import pytest
from source_criteo.streams import CriteoStream


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(CriteoStream, "path", "2023-01/statistics/report")
    mocker.patch.object(CriteoStream, "primary_key", "test_primary_key")
    mocker.patch.object(CriteoStream, "__abstractmethods__", set())

    return {
        "config": {
            "advertiserIds": "10817,10398",
            "start_date": datetime.datetime.strftime((datetime.datetime.now() - datetime.timedelta(days=1)), "%Y-%m-%d"),
            "end_date": datetime.datetime.strftime((datetime.datetime.now()), "%Y-%m-%d"),
            "dimensions": ["AdvertiserId", "Os", "Day"],
            "metrics": ["Displays", "Clicks"],
            "currency": "EUR",
            "timezone": "Europe/Rome",
            "lookback_window": 1,
        }
    }


def test_request_params(patch_base_class):
    assert (
        CriteoStream(authenticator=MagicMock(), **patch_base_class["config"]).request_params(
            stream_state=MagicMock(), stream_slice=MagicMock(), next_page_token=MagicMock()
        )
        == {}
    )


def test_parse_response(patch_base_class):
    stream = CriteoStream(authenticator=MagicMock(), **patch_base_class["config"])
    response_data = {
        "Total": {"Displays": "87", "Clicks": "50"},
        "Rows": [
            {"AdvertiserId": "10398", "Os": "Other", "Day": "2023-04-14", "Currency": "EUR", "Displays": "85", "Clicks": "0"},
            {"AdvertiserId": "10817", "Os": "Other", "Day": "2023-04-14", "Currency": "EUR", "Displays": "2", "Clicks": "50"},
        ],
    }

    expected_data = [
        {"AdvertiserId": "10398", "Os": "Other", "Day": "2023-04-14", "Currency": "EUR", "Displays": "85", "Clicks": "0"},
        {"AdvertiserId": "10817", "Os": "Other", "Day": "2023-04-14", "Currency": "EUR", "Displays": "2", "Clicks": "50"},
    ]

    response = MagicMock()
    response.json.return_value = response_data
    inputs = {"response": response, "stream_state": {}}
    actual_records: Mapping[str, Any] = list(stream.parse_response(**inputs))
    assert actual_records == expected_data


def test_request_headers(patch_base_class):
    stream = CriteoStream(authenticator=MagicMock(), **patch_base_class["config"])
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = CriteoStream(authenticator=MagicMock(), **patch_base_class["config"])
    expected_method = "POST"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "should_retry"),
    [
        (HTTPStatus.OK, False),
        (HTTPStatus.BAD_REQUEST, False),
        (HTTPStatus.TOO_MANY_REQUESTS, True),
        (HTTPStatus.INTERNAL_SERVER_ERROR, True),
    ],
)
def test_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = CriteoStream(authenticator=MagicMock(), **patch_base_class["config"])
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = CriteoStream(authenticator=MagicMock(), **patch_base_class["config"])
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
