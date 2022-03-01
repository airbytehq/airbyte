#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#

from http import HTTPStatus
from unittest.mock import MagicMock

import pytest

from airbyte_cdk.sources.streams.http.auth.core import NoAuth

from source_apple_search_ads.basic_streams import AppleSearchAdsStream, Campaigns

DEFAULT_CONFIG = {
  "org_id": "org_id"
}

@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(AppleSearchAdsStream, "path", "v0/example_endpoint")
    mocker.patch.object(AppleSearchAdsStream, "primary_key", "test_primary_key")
    mocker.patch.object(AppleSearchAdsStream, "__abstractmethods__", set())


def test_campaigns_request_params(patch_base_class):
    stream = Campaigns(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)

    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {"limit": 1000, "offset": 0}

    assert stream.request_params(**inputs) == expected_params


def test_campaigns_next_page_token(patch_base_class):
    stream = Campaigns(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)

    response = MagicMock()
    response.json.return_value = {"pagination": {"totalResults": 100, "startIndex": 0, "itemsPerPage": 10}}
    inputs = {"response": response}
    expected_token = {"limit": 1000, "offset": 10}

    assert stream.next_page_token(**inputs) == expected_token


def test_campaigns_parse_response(patch_base_class):
    stream = Campaigns(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)

    records = [
        {"key": "value"},
        {"key": "value2"},
    ]
    response = MagicMock()
    response.json.return_value = {"data": records}
    inputs = {"response": response}
    expected_parsed_object = records

    assert list(stream.parse_response(**inputs)) == expected_parsed_object


def test_campaigns_request_headers(patch_base_class):
    stream = Campaigns(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {'X-AP-Context': f"orgId={DEFAULT_CONFIG['org_id']}"}
    assert stream.request_headers(**inputs) == expected_headers


def test_campaigns_http_method(patch_base_class):
    stream = Campaigns(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)
    expected_method = "GET"
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
def test_campaigns_should_retry(patch_base_class, http_status, should_retry):
    response_mock = MagicMock()
    response_mock.status_code = http_status
    stream = Campaigns(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)
    assert stream.should_retry(response_mock) == should_retry


def test_campaigns_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = Campaigns(org_id=DEFAULT_CONFIG["org_id"], authenticator=NoAuth)
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time
