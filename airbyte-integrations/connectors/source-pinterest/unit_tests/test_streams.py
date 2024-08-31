#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from http import HTTPStatus
from unittest.mock import MagicMock, patch

import pytest
import requests
from airbyte_cdk import AirbyteTracedException
from airbyte_cdk.models.airbyte_protocol import SyncMode
from airbyte_cdk.sources.declarative.types import StreamSlice
from airbyte_cdk.sources.streams.http.error_handlers import ResponseAction
from source_pinterest.streams import (
    AnalyticsApiBackoffStrategyDecorator,
    NonJSONResponse,
    PinterestAnalyticsStream,
    PinterestErrorHandler,
    PinterestStream,
    PinterestSubStream,
)
from source_pinterest.utils import get_analytics_columns

from .conftest import get_stream_by_name
from .utils import create_requests_response

os.environ["REQUEST_CACHE_PATH"] = "/tmp"
_ANY_STREAM_NAME = "any_stream_name"
_RETRY_AFTER_HEADER = "XRetry-After"
_A_MAX_TIME = 10


@pytest.fixture
def patch_base_class(mocker):
    # Mock abstract methods to enable instantiating abstract class
    mocker.patch.object(PinterestStream, "path", "v0/example_endpoint")
    mocker.patch.object(PinterestStream, "primary_key", "test_primary_key")
    mocker.patch.object(PinterestStream, "__abstractmethods__", set())
    #
    mocker.patch.object(PinterestSubStream, "path", "v0/example_endpoint")
    mocker.patch.object(PinterestSubStream, "primary_key", "test_primary_key")
    mocker.patch.object(PinterestSubStream, "next_page_token", None)
    mocker.patch.object(PinterestSubStream, "parse_response", {})
    mocker.patch.object(PinterestSubStream, "__abstractmethods__", set())
    #
    mocker.patch.object(PinterestAnalyticsStream, "path", "v0/example_endpoint")
    mocker.patch.object(PinterestAnalyticsStream, "primary_key", "test_primary_key")
    mocker.patch.object(PinterestAnalyticsStream, "next_page_token", None)
    mocker.patch.object(PinterestAnalyticsStream, "parse_response", {})
    mocker.patch.object(PinterestAnalyticsStream, "__abstractmethods__", set())


def test_request_params(patch_base_class):
    stream = PinterestStream(config=MagicMock())
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_params = {}
    assert stream.request_params(**inputs) == expected_params


def test_next_page_token(patch_base_class, test_response):
    stream = PinterestStream(config=MagicMock())
    inputs = {"response": test_response}
    expected_token = {"bookmark": "string"}
    assert stream.next_page_token(**inputs) == expected_token


def test_parse_response(patch_base_class, test_response, test_current_stream_state):
    stream = PinterestStream(config=MagicMock())
    inputs = {"response": test_response, "stream_state": test_current_stream_state}
    expected_parsed_object = {}
    assert next(stream.parse_response(**inputs)) == expected_parsed_object


def test_parse_response_with_sensitive_data(requests_mock, test_config):
    """Test that sensitive data is removed"""
    stream = get_stream_by_name("catalogs_feeds", test_config)
    requests_mock.get(
        url="https://api.pinterest.com/v5/catalogs/feeds",
        json={"items": [{"id": "CatalogsFeeds1", "credentials": {"password": "bla"}}]},
    )
    actual_response = [
        dict(record) for stream_slice in stream.stream_slices(sync_mode=SyncMode.full_refresh)
        for record in stream.read_records(sync_mode=SyncMode.full_refresh, stream_slice=stream_slice)
    ]
    assert actual_response == [{"id": "CatalogsFeeds1"}]


def test_request_headers(patch_base_class):
    stream = PinterestStream(config=MagicMock())
    inputs = {"stream_slice": None, "stream_state": None, "next_page_token": None}
    expected_headers = {}
    assert stream.request_headers(**inputs) == expected_headers


def test_http_method(patch_base_class):
    stream = PinterestStream(config=MagicMock())
    expected_method = "GET"
    assert stream.http_method == expected_method


@pytest.mark.parametrize(
    ("http_status", "expected_response_action"),
    (
        (HTTPStatus.OK, ResponseAction.SUCCESS),
        (HTTPStatus.BAD_REQUEST, ResponseAction.FAIL),
        (HTTPStatus.TOO_MANY_REQUESTS, ResponseAction.RETRY),
        (HTTPStatus.INTERNAL_SERVER_ERROR, ResponseAction.RETRY),
    ),
)
def test_response_action(requests_mock, patch_base_class, http_status, expected_response_action):
    response_mock = create_requests_response(requests_mock, http_status, {})
    stream = PinterestStream(config=MagicMock())
    assert stream._http_client._error_handler.interpret_response(response_mock).response_action == expected_response_action


@pytest.mark.parametrize(
    ("test_response", "status_code", "expected_response_action"),
    (
        ({"code": 8, "message": "You have exceeded your rate limit. Try again later."}, 429, ResponseAction.RETRY),
        ({"message": "You got data!"}, 200, ResponseAction.SUCCESS),
    ),
)
@patch("time.sleep", return_value=None)
def test_declarative_stream_response_action_on_max_rate_limit_error(mock_sleep, requests_mock, test_response, status_code, expected_response_action):
    response_mock = create_requests_response(requests_mock, status_code, {})
    error_handler = PinterestErrorHandler(logger=MagicMock(), stream_name="any_stream_name")
    assert error_handler.interpret_response(response_mock).response_action == expected_response_action


def test_non_json_response(requests_mock, patch_base_class):
    url = "https://api.pinterest.com/v5/boards"
    requests_mock.get(url, text="some response", status_code=200)
    response_mock = requests.get(url)
    error_handler = PinterestErrorHandler(logger=MagicMock(), stream_name="any_stream_name")

    with pytest.raises(NonJSONResponse) as exception:
        error_handler.interpret_response(response_mock).response_action == ResponseAction.RETRY
    assert "Received unexpected response in non json format" in str(exception)


@pytest.mark.parametrize(("response", "expected_backoff_time"), (({"code": 1}, 1),))
def test_analytics_stream_backoff_time(requests_mock, response, expected_backoff_time):
    url = "https://api.pinterest.com/v5/boards"
    requests_mock.get(
        url,
        json={"code": 1},
        status_code=400,
    )
    response = requests.get(url)

    assert AnalyticsApiBackoffStrategyDecorator().backoff_time(response) == 1


def test_analytics_stream_request_params(patch_base_class):
    stream = PinterestAnalyticsStream(parent=None, config=MagicMock())
    stream.analytics_target_ids = "target_id"
    stream_slice = {"start_date": "2024-04-04", "end_date": "2024-04-05", "parent": {"id": "parent_id"}}
    expected_params = {
        "start_date": "2024-04-04",
        "end_date": "2024-04-05",
        "granularity": "DAY",
        "columns": get_analytics_columns(),
        "target_id": "parent_id",
    }
    assert stream.request_params(stream_state={}, stream_slice=stream_slice) == expected_params


@pytest.mark.parametrize(
    ("stream_name", "stream_slice", "expected_path"),
    (
        ("boards", None, "boards"),
        ("ad_accounts", None, "ad_accounts"),
        ("board_sections", {"id": "123"}, "boards/123/sections"),
        ("board_pins", {"id": "123"}, "boards/123/pins"),
        ("board_section_pins", {"parent_slice": {"id": "234"}, "id": "123"}, "boards/234/sections/123/pins"),
        ("ad_account_analytics", {"id": "123"}, "ad_accounts/123/analytics"),
        ("campaigns", {"id": "123"}, "ad_accounts/123/campaigns"),
        (
            "campaign_analytics",
            {"parent_slice": {"id": "234"}, "id": "123"},
            "ad_accounts/234/campaigns/analytics?campaign_ids=123",
        ),
        ("ad_groups", {"id": "123"}, "ad_accounts/123/ad_groups"),
        (
            "ad_group_analytics",
            {"parent_slice": {"id": "234"}, "id": "123"},
            "ad_accounts/234/ad_groups/analytics?ad_group_ids=123",
        ),
        ("ads", {"id": "123"}, "ad_accounts/123/ads"),
        ("ad_analytics", {"parent_slice": {"id": "234"}, "id": "123"}, "ad_accounts/234/ads/analytics?ad_ids=123"),
        ("catalogs", None, "catalogs"),
        ("catalogs_feeds", None, "catalogs/feeds"),
        ("catalogs_product_groups", None, "catalogs/product_groups"),
        (
            "keywords",
            {"parent_slice": {"id": "AD_ACCOUNT_1"}, "id": "234"},
            "ad_accounts/AD_ACCOUNT_1/keywords?ad_group_id=234",
        ),
        ("audiences", {"id": "AD_ACCOUNT_1"}, "ad_accounts/AD_ACCOUNT_1/audiences"),
        ("conversion_tags", {"id": "AD_ACCOUNT_1"}, "ad_accounts/AD_ACCOUNT_1/conversion_tags"),
        ("customer_lists", {"id": "AD_ACCOUNT_1"}, "ad_accounts/AD_ACCOUNT_1/customer_lists"),
    ),
)
def test_path(test_config, stream_name, stream_slice, expected_path):
    stream = get_stream_by_name(stream_name, test_config)
    if stream_slice:
        stream_slice = StreamSlice(partition=stream_slice, cursor_slice={})

    result = stream.retriever.requester.get_path(stream_slice=stream_slice, stream_state=None, next_page_token=None)
    assert result == expected_path
