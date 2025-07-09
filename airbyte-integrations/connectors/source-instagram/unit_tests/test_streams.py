#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from datetime import datetime
from unittest.mock import MagicMock

import pytest
from facebook_business import FacebookAdsApi, FacebookSession

from airbyte_cdk.models import SyncMode
from airbyte_cdk.sources.types import StreamSlice

from .conftest import find_stream
from .utils import read_full_refresh, read_incremental


FB_API_VERSION = FacebookAdsApi.API_VERSION


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
# todo: user_insights should probably be a dedicated mocked request not a fixtrue?
def test_user_insights_state(requests_mock, user_insights, values, slice_dates, expected):
    """
    This test shows how `STATE` is managed based on the scenario for Incremental Read.
    """
    config = {"start_date": "2023-01-01T01:01:01Z"}

    requests_mock.get(
        "",
    )

    # UserInsights stream
    stream = find_stream(stream_name="user_insights", config=config)
    # Populate the fixute with `values`
    # user_insights(values)
    # simulate `read_recods` generator job
    list(
        stream.read_records(
            sync_mode=SyncMode.incremental,
            stream_slice=StreamSlice(
                partition={"instagram_business_account": "123"}, cursor_slice={**slice_dates}, extra_fields={"page_id": 1}
            ),
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

    stream = find_stream(stream_name="user_insights", config=config)
    records = read_full_refresh(stream)

    assert records


def test_exit_gracefully(api, config, requests_mock, caplog):
    test_id = "test_id"
    stream = find_stream(stream_name="user_insights", config=config)
    requests_mock.register_uri("GET", FacebookSession.GRAPH + f"/{FB_API_VERSION}/{test_id}/insights", json={"data": []})
    records = read_incremental(stream, {})
    assert not records
    assert requests_mock.call_count == 6  # 4 * 1 per `metric_to_period` map + 1 `summary` request + 1 `business_account_id` request
    assert "Stopping syncing stream 'user_insights'" in caplog.text
