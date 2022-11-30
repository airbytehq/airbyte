#
# Copyright (c) 2022 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from facebook_business import FacebookAdsApi, FacebookSession
from source_instagram.streams import (
    InstagramStream,
    Media,
    MediaInsights,
    Stories,
    StoryInsights,
    UserInsights,
    UserLifetimeInsights,
    Users,
)
from utils import read_full_refresh, read_incremental

FB_API_VERSION = FacebookAdsApi.API_VERSION


def test_clear_url(config):
    media_url = "https://google.com?_nc_rid=123"
    profile_picture_url = "https://google.com?ccb=123"

    expected = {"media_url": "https://google.com", "profile_picture_url": "https://google.com"}
    assert InstagramStream._clear_url({"media_url": media_url, "profile_picture_url": profile_picture_url}) == expected


def test_state_outdated(api, config):
    assert UserInsights(api=api, start_date=datetime.strptime(config["start_date"], "%Y-%m-%dT%H:%M:%S"))._state_has_legacy_format(
        {"state": MagicMock()}
    )


def test_state_is_not_outdated(api, config):
    assert not UserInsights(api=api, start_date=datetime.strptime(config["start_date"], "%Y-%m-%dT%H:%M:%S"))._state_has_legacy_format(
        {"state": {}}
    )


def test_media_get_children(api, requests_mock, some_config):
    test_id = "test_id"
    expected = {"id": "test_id"}

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/", [{}])

    assert next(Media(api=api)._get_children([test_id])) == expected


def test_media_read(api, user_stories_data, requests_mock):
    test_id = "test_id"
    stream = Media(api=api)

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/media", [{"json": user_stories_data}])

    records = read_full_refresh(stream)
    assert records == [{"business_account_id": "test_id", "id": "test_id", "page_id": "act_unknown_account"}]


def test_media_insights_read(api, user_stories_data, user_media_insights_data, requests_mock):
    test_id = "test_id"
    stream = MediaInsights(api=api)

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/media", [{"json": user_stories_data}])
    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/insights", [{"json": user_media_insights_data}])

    records = read_full_refresh(stream)
    assert records == [{"business_account_id": "test_id", "id": "test_id", "impressions": 264, "page_id": "act_unknown_account"}]


def test_user_read(api, user_data, requests_mock):
    test_id = "test_id"
    stream = Users(api=api)

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/", [{"json": user_data}])

    records = read_full_refresh(stream)
    assert records == [
        {
            "biography": "Dino data crunching app",
            "id": "17841405822304914",
            "page_id": "act_unknown_account",
            "username": "metricsaurus",
            "website": "http://www.metricsaurus.com/",
        }
    ]


def test_user_insights_read(api, config, user_insight_data, requests_mock):
    test_id = "test_id"

    stream = UserInsights(api=api, start_date=datetime.strptime(config["start_date"], "%Y-%m-%dT%H:%M:%S"))

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/insights", [{"json": user_insight_data}])

    records = read_incremental(stream, {})
    assert records


def test_user_lifetime_insights_read(api, config, user_insight_data, requests_mock):
    test_id = "test_id"

    stream = UserLifetimeInsights(api=api)

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/insights", [{"json": user_insight_data}])

    records = read_full_refresh(stream)
    assert records == [
        {
            "page_id": "act_unknown_account",
            "business_account_id": "test_id",
            "metric": "impressions",
            "date": "2020-05-04T07:00:00+0000",
            "value": 4,
        }
    ]


def test_stories_read(api, requests_mock, user_stories_data):
    test_id = "test_id"
    stream = Stories(api=api)

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/stories", [{"json": user_stories_data}])

    records = read_full_refresh(stream)
    assert records == [{"business_account_id": "test_id", "id": "test_id", "page_id": "act_unknown_account"}]


def test_stories_insights_read(api, requests_mock, user_stories_data, user_media_insights_data):
    test_id = "test_id"
    stream = StoryInsights(api=api)

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/stories", [{"json": user_stories_data}])
    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/insights", [{"json": user_media_insights_data}])

    records = read_full_refresh(stream)
    assert records == [{"business_account_id": "test_id", "id": "test_id", "impressions": 264, "page_id": "act_unknown_account"}]


@pytest.mark.parametrize(
    "error_response",
    [
        {"json": {"error": {"type": "OAuthException", "code": 1}}},
        {"json": {"error": {"code": 4}}},
        {"json": {}, "status_code": 429},
        {"json": {"error": {"type": "OAuthException", "message": "(#10) Not enough viewers for the media to show insights", "code": 10}}},
        {"json": {"error": {"code": 100, "error_subcode": 33}}, "status_code": 400},
        {"json": {"error": {"is_transient": True}}},
        {"json": {"error": {"code": 4, "error_subcode": 2108006}}},
    ],
    ids=[
        "oauth_error",
        "rate_limit_error",
        "too_many_request_error",
        "viewers_insights_error",
        "4028_issue_error",
        "transient_error",
        "user_media_creation_time_error",
    ],
)
def test_common_error_retry(error_response, requests_mock, api, account_id):
    """Error once, check that we retry and not fail"""
    response = {"business_account_id": "test_id", "page_id": "act_unknown_account"}
    responses = [
        error_response,
        {
            "json": response,
            "status_code": 200,
        },
    ]
    test_id = "test_id"
    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/media", responses)

    stream = Media(api=api)
    records = read_full_refresh(stream)

    assert [response] == records
