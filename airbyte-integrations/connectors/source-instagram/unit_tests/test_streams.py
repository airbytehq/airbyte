#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import SyncMode
from facebook_business import FacebookAdsApi, FacebookSession
from source_instagram.streams import (
    DatetimeTransformerMixin,
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
    assert UserInsights(api=api, start_date=config["start_date"])._state_has_legacy_format({"state": MagicMock()})


def test_state_is_not_outdated(api, config):
    assert not UserInsights(api=api, start_date=config["start_date"])._state_has_legacy_format({"state": {}})


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


def test_media_insights_read_error(api, requests_mock):
    test_id = "test_id"
    stream = MediaInsights(api=api)
    media_response = [{"id": "test_id"}, {"id": "test_id_2"}, {"id": "test_id_3"}, {"id": "test_id_4"}, {"id": "test_id_5"}]
    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/media", json={"data": media_response})

    media_insights_response_test_id = {
        "name": "impressions",
        "period": "lifetime",
        "values": [{"value": 264}],
        "title": "Impressions",
        "description": "Total number of times the media object has been seen",
        "id": "test_id/insights/impressions/lifetime",
    }
    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/insights", json=media_insights_response_test_id)

    error_response_oauth = {
        "error": {
            "message": "Invalid parameter",
            "type": "OAuthException",
            "code": 100,
            "error_data": {},
            "error_subcode": 2108006,
            "is_transient": False,
            "error_user_title": "Media posted before business account conversion",
            "error_user_msg": "The media was posted before the most recent time that the user's account was converted to a business account from a personal account.",
            "fbtrace_id": "fake_trace_id",
        }
    }
    requests_mock.register_uri(
        "GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/test_id_2/insights", json=error_response_oauth, status_code=400
    )

    error_response_wrong_permissions = {
        "error": {
            "message": "Invalid parameter",
            "type": "OAuthException",
            "code": 100,
            "error_data": {},
            "error_subcode": 33,
            "is_transient": False,
            "error_user_msg": "Unsupported get request. Object with ID 'test_id_3' does not exist, cannot be loaded due to missing permissions, or does not support this operation.",
            "fbtrace_id": "fake_trace_id",
        }
    }
    requests_mock.register_uri(
        "GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/test_id_3/insights", json=error_response_wrong_permissions, status_code=400
    )

    media_insights_response_test_id_4 = {
        "name": "impressions",
        "period": "lifetime",
        "values": [{"value": 300}],
        "title": "Impressions",
        "description": "Total number of times the media object has been seen",
        "id": "test_id_3/insights/impressions/lifetime",
    }
    requests_mock.register_uri(
        "GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/test_id_4/insights", json=media_insights_response_test_id_4
    )

    error_response_wrong_permissions_code_10 = {
        "error": {
            "message": "(#10) Application does not have permission for this action",
            "type": "OAuthException",
            "code": 10,
            "fbtrace_id": "fake_trace_id",
        }
    }
    requests_mock.register_uri(
        "GET",
        FacebookSession.GRAPH + f"/{FB_API_VERSION}/test_id_5/insights",
        json=error_response_wrong_permissions_code_10,
        status_code=400,
    )

    records = read_full_refresh(stream)
    expected_records = [
        {"business_account_id": "test_id", "id": "test_id", "impressions": 264, "page_id": "act_unknown_account"},
        {"business_account_id": "test_id", "id": "test_id_4", "impressions": 300, "page_id": "act_unknown_account"},
    ]
    assert records == expected_records


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

    stream = UserInsights(api=api, start_date=config["start_date"])

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/insights", [{"json": user_insight_data}])

    records = read_incremental(stream, {})
    assert records


def test_user_lifetime_insights_read(api, config, user_lifetime_insight_data, requests_mock):
    test_id = "test_id"

    stream = UserLifetimeInsights(api=api)

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/insights", [{"json": user_lifetime_insight_data}])

    records = read_full_refresh(stream)
    expected_record = {
        "breakdown": "city",
        "business_account_id": "test_id",
        "metric": "impressions",
        "page_id": "act_unknown_account",
        "value": {"London, England": 22, "Sydney, New South Wales": 33}
    }
    assert expected_record in records


@pytest.mark.parametrize(
    "values,slice_dates,expected",
    [
        # the state is updated to the value of `end_time`
        (
            {"end_time": "2023-01-01 00:01:00", "value": {"one": 1}},
            {"since": "2023-01-01 00:01:00", "until": "2023-01-02 00:01:00"},
            {"123": {"date": "2023-01-01T00:01:00+00:00"}},
        ),
        # the state is taken from `start_date`
        (
            {"end_time": None, "value": {"two": 2}},
            {"since": "2023-01-01 00:00:00", "until": "2023-01-02 00:01:00"},
            # state from `start_date` is expected
            {"123": {"date": "2023-01-01T01:01:01+00:00"}},
        ),
        # the state is updated to the value of `end_time`
        (
            {"end_time": "2023-02-02 00:02:00", "value": None},
            {"since": "2023-06-01 21:00:00", "until": "2023-06-02 22:00:00"},
            {"123": {"date": "2023-02-02T00:02:00+00:00"}},
        ),
        # the state is taken from `start_date`
        (
            {"end_time": None, "value": None},
            {"since": "2023-06-01 21:00:00", "until": "2023-06-02 22:00:00"},
            {"123": {"date": "2023-01-01T01:01:01+00:00"}},
        ),
    ],
    ids=[
        "Normal state flow",
        "No `end_time` value in record",
        "No `value` in record",
        "No `end_time` and no `value` in record",
    ],
)
def test_user_insights_state(api, user_insights, values, slice_dates, expected):
    """
    This test shows how `STATE` is managed based on the scenario for Incremental Read.
    """
    import pendulum

    # UserInsights stream
    stream = UserInsights(api=api, start_date="2023-01-01T01:01:01Z")
    # Populate the fixute with `values`
    user_insights(values)
    # simulate `read_recods` generator job
    list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice={"account": {"page_id": 1, "instagram_business_account": user_insights}, **slice_dates},
        )
    )
    assert stream.state == expected


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
        {
            "json": {"error": {"code": 1, "message": "Please reduce the amount of data you're asking for, then retry your request"}},
            "status_code": 500,
        },
        {"json": {"error": {"code": 1, "message": "An unknown error occurred"}}, "status_code": 500},
        {"json": {"error": {"type": "OAuthException", "message": "(#10) Not enough viewers for the media to show insights", "code": 10}}},
        {"json": {"error": {"code": 100, "error_subcode": 33}}, "status_code": 400},
        {"json": {"error": {"is_transient": True}}},
        {"json": {"error": {"code": 4, "error_subcode": 2108006}}},
    ],
    ids=[
        "oauth_error",
        "rate_limit_error",
        "too_many_request_error",
        "reduce_amount_of_data_error",
        "unknown_error",
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


def test_exit_gracefully(api, config, requests_mock, caplog):
    test_id = "test_id"
    stream = UserInsights(api=api, start_date=config["start_date"])
    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/insights", json={"data": []})
    records = read_incremental(stream, {})
    assert not records
    assert requests_mock.call_count == 6  # 4 * 1 per `metric_to_period` map + 1 `summary` request + 1 `business_account_id` request
    assert "Stopping syncing stream 'user_insights'" in caplog.text


@pytest.mark.parametrize(
    "original_value, field_schema, expected",
    [
        ("2020-01-01T12:00:00Z", {"format": "date-time", "airbyte_type": "timestamp_with_timezone"}, "2020-01-01T12:00:00+00:00"),
        ("2020-05-04T07:00:00+0000", {"format": "date-time", "airbyte_type": "timestamp_with_timezone"}, "2020-05-04T07:00:00+00:00"),
        (None, {"format": "date-time", "airbyte_type": "timestamp_with_timezone"}, None),
        ("2020-01-01T12:00:00", {"format": "date-time", "airbyte_type": "timestamp_without_timezone"}, "2020-01-01T12:00:00"),
        ("2020-01-01T14:00:00", {"format": "date-time"}, "2020-01-01T14:00:00"),
        ("2020-02-03T12:00:00", {"type": "string"}, "2020-02-03T12:00:00"),
    ],
)
def test_custom_transform_datetime_rfc3339(original_value, field_schema, expected):
    # Call the static method
    result = DatetimeTransformerMixin.custom_transform_datetime_rfc3339(original_value, field_schema)

    # Assert the result matches the expected output
    assert result == expected
