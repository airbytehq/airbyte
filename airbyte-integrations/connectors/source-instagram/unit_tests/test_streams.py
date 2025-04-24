#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from facebook_business import FacebookAdsApi, FacebookSession
from source_instagram.streams import DatetimeTransformerMixin, InstagramStream, UserInsights
from utils import read_full_refresh, read_incremental

from airbyte_cdk.models import SyncMode


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


def test_user_insights_read(api, config, user_insight_data, requests_mock):
    test_id = "test_id"

    stream = UserInsights(api=api, start_date=config["start_date"])

    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/insights", [{"json": user_insight_data}])

    records = read_incremental(stream, {})
    assert records


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
def test_common_error_retry(config, error_response, requests_mock, api, account_id, user_insight_data):
    """Error once, check that we retry and not fail"""
    # response = {"business_account_id": "test_id", "page_id": "act_unknown_account"}
    responses = [
        error_response,
        {
            "json": user_insight_data,
            "status_code": 200,
        },
    ]
    test_id = "test_id"
    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/insights", responses)

    stream = UserInsights(api=api, start_date=config["start_date"])
    records = read_full_refresh(stream)

    assert records


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
