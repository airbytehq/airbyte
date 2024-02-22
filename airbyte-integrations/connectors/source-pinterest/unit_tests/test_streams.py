#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import os
from http import HTTPStatus
from unittest.mock import MagicMock

import pytest
import requests
from source_pinterest.streams import (
    AdAccountAnalytics,
    AdAccounts,
    AdAnalytics,
    AdGroupAnalytics,
    AdGroups,
    Ads,
    Audiences,
    BoardPins,
    Boards,
    BoardSectionPins,
    BoardSections,
    CampaignAnalytics,
    Campaigns,
    Catalogs,
    CatalogsFeeds,
    CatalogsProductGroups,
    ConversionTags,
    CustomerLists,
    Keywords,
    PinterestStream,
    PinterestSubStream,
    RateLimitExceeded,
    UserAccountAnalytics,
)

os.environ["REQUEST_CACHE_PATH"] = "/tmp"


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


def test_parse_response_with_sensitive_data(patch_base_class):
    """Test that sensitive data is removed"""
    stream = CatalogsFeeds(config=MagicMock())
    response = MagicMock()
    response.json.return_value = {"items": [{"id": "CatalogsFeeds1", "credentials": {"password": "bla"}}], "bookmark": "string"}
    actual_response = list(stream.parse_response(response=response, stream_state=None))
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
    stream = PinterestStream(config=MagicMock())
    assert stream.should_retry(response_mock) == should_retry


def test_backoff_time(patch_base_class):
    response_mock = MagicMock()
    stream = PinterestStream(config=MagicMock())
    expected_backoff_time = None
    assert stream.backoff_time(response_mock) == expected_backoff_time


@pytest.mark.parametrize(
    "test_response, status_code, expected",
    [
        ({"code": 8, "message": "You have exceeded your rate limit. Try again later."}, 429, False),
        ({"code": 7, "message": "Some other error message"}, 429, False),
    ],
)
def test_should_retry_on_max_rate_limit_error(requests_mock, test_response, status_code, expected):
    stream = Boards(config=MagicMock())
    url = "https://api.pinterest.com/v5/boards"
    requests_mock.get("https://api.pinterest.com/v5/boards", json=test_response, status_code=status_code)
    response = requests.get(url)
    result = stream.should_retry(response)
    assert result == expected


def test_non_json_response(requests_mock):
    stream = UserAccountAnalytics(parent=None, config=MagicMock())
    url = "https://api.pinterest.com/v5/boards"
    requests_mock.get("https://api.pinterest.com/v5/boards", text="some response", status_code=200)
    response = requests.get(url)
    try:
        stream.should_retry(response)
        assert False
    except Exception as e:
        assert "Received unexpected response in non json format" in str(e)


@pytest.mark.parametrize(
    "test_response, test_headers, status_code, expected",
    [
        ({"code": 7, "message": "Some other error message"}, {"X-RateLimit-Reset": "2"}, 429, 2.0),
        (
            {"code": 7, "message": "Some other error message"},
            {"X-RateLimit-Reset": "2000"},
            429,
            (RateLimitExceeded, "Rate limit exceeded for stream boards. Waiting time is longer than 10 minutes: 2000.0s."),
        ),
    ],
)
def test_backoff_on_rate_limit_error(requests_mock, test_response, status_code, test_headers, expected):
    stream = Boards(config=MagicMock())
    url = "https://api.pinterest.com/v5/boards"
    requests_mock.get(
        "https://api.pinterest.com/v5/boards",
        json=test_response,
        headers=test_headers,
        status_code=status_code,
    )

    response = requests.get(url)

    if isinstance(expected, tuple):
        with pytest.raises(expected[0], match=expected[1]):
            stream.backoff_time(response)
    else:
        result = stream.backoff_time(response)
        assert result == expected


@pytest.mark.parametrize(
    ("stream_cls, slice, expected"),
    [
        (Boards(MagicMock()), None, "boards"),
        (AdAccounts(MagicMock()), None, "ad_accounts"),
        (BoardSections(parent=None, config=MagicMock()), {"parent": {"id": "123"}}, "boards/123/sections"),
        (BoardPins(parent=None, config=MagicMock()), {"parent": {"id": "123"}}, "boards/123/pins"),
        (
            BoardSectionPins(parent=None, config=MagicMock()),
            {"sub_parent": {"parent": {"id": "234"}}, "parent": {"id": "123"}},
            "boards/234/sections/123/pins",
        ),
        (AdAccountAnalytics(parent=None, config=MagicMock()), {"parent": {"id": "123"}}, "ad_accounts/123/analytics"),
        (Campaigns(parent=None, config=MagicMock()), {"parent": {"id": "123"}}, "ad_accounts/123/campaigns"),
        (
            CampaignAnalytics(parent=None, config=MagicMock()),
            {"sub_parent": {"parent": {"id": "234"}}, "parent": {"id": "123"}},
            "ad_accounts/234/campaigns/analytics",
        ),
        (AdGroups(parent=None, config=MagicMock()), {"parent": {"id": "123"}}, "ad_accounts/123/ad_groups"),
        (
            AdGroupAnalytics(parent=None, config=MagicMock()),
            {"sub_parent": {"parent": {"id": "234"}}, "parent": {"id": "123"}},
            "ad_accounts/234/ad_groups/analytics",
        ),
        (Ads(parent=None, config=MagicMock()), {"parent": {"id": "123"}}, "ad_accounts/123/ads"),
        (
            AdAnalytics(parent=None, config=MagicMock()),
            {"sub_parent": {"parent": {"id": "234"}}, "parent": {"id": "123"}},
            "ad_accounts/234/ads/analytics",
        ),
        (Catalogs(config=MagicMock()), None, "catalogs"),
        (CatalogsFeeds(config=MagicMock()), None, "catalogs/feeds"),
        (CatalogsProductGroups(config=MagicMock()), None, "catalogs/product_groups"),
        (
            Keywords(parent=None, config=MagicMock()),
            {"parent": {"id": "234", "ad_account_id": "AD_ACCOUNT_1"}},
            "ad_accounts/AD_ACCOUNT_1/keywords?ad_group_id=234",
        ),
        (Audiences(parent=None, config=MagicMock()), {"parent": {"id": "AD_ACCOUNT_1"}}, "ad_accounts/AD_ACCOUNT_1/audiences"),
        (ConversionTags(parent=None, config=MagicMock()), {"parent": {"id": "AD_ACCOUNT_1"}}, "ad_accounts/AD_ACCOUNT_1/conversion_tags"),
        (CustomerLists(parent=None, config=MagicMock()), {"parent": {"id": "AD_ACCOUNT_1"}}, "ad_accounts/AD_ACCOUNT_1/customer_lists"),
    ],
)
def test_path(patch_base_class, stream_cls, slice, expected):
    stream = stream_cls
    if slice:
        result = stream.path(stream_slice=slice)
    else:
        result = stream.path()
    assert result == expected
