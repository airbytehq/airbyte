#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#
import logging
from typing import Any, Mapping, Optional

import freezegun
import pytest

from airbyte_cdk.logger import init_logger
from airbyte_cdk.sources.streams.call_rate import HttpAPIBudget

from .conftest import GRAPH_URL, account_url, find_stream
from .utils import read_full_refresh


# can we make this only initialized once
def mock_accounts_request(requests_mock, some_config):
    requests_mock.register_uri(
        "GET",
        account_url,
        json={"data": [{"id": "page_id", "instagram_business_account": {"id": "instagram_business_account_id"}}]},
    )


def mock_user_insights_day_request(requests_mock, values, error_response: Optional[Mapping[str, Any]] = None):
    responses = []
    if error_response:
        responses.append(error_response)

    responses.append(
        {
            "json": {
                "data": [
                    {
                        "description": "test_insight",
                        "id": "123",
                        "name": "test_insight_metric",
                        "period": "day",
                        "title": "Test Insight",
                        "values": [values],
                    }
                ]
            },
            "status_code": 200,
        }
    )

    requests_mock.register_uri(
        "GET",
        f"{GRAPH_URL}/instagram_business_account_id/insights?period=day&metric=follower_count%2Creach",
        responses,
    )


def mock_user_insights_requests(requests_mock, values):
    period_to_metrics = {
        "week": "reach",
        "days_28": "reach",
        "lifetime": "online_followers",
    }
    for period, metrics in period_to_metrics.items():
        response = {
            "data": [
                {
                    "description": "test_insight",
                    "id": "123",
                    "name": "test_insight_metric",
                    "period": period,
                    "title": "Test Insight",
                    "values": [values],
                }
            ]
        }

        requests_mock.register_uri(
            "GET",
            f"{GRAPH_URL}/instagram_business_account_id/insights?period={period}&metric={metrics}",
            json=response,
        )


@pytest.mark.parametrize(
    "values,slice_dates,expected",
    [
        # the state is updated to the value of `end_time`
        pytest.param(
            {"end_time": "2025-07-01 07:00:00+0000", "value": {"one": 1}},
            {"start_time": "2025-07-01T00:00:00+00:00", "end_time": "2025-07-01T23:59:59+00:00"},
            {
                "lookback_window": 0,
                "state": {"date": "2025-07-01T07:00:00+00:00"},
                "states": [
                    {"cursor": {"date": "2025-07-01T07:00:00+00:00"}, "partition": {"business_account_id": "instagram_business_account_id"}}
                ],
                "use_global_cursor": False,
                "parent_state": {},
            },
            id="test_normal_state_flow",
        ),
        # the state checkpoints at `start_date` for the partition
        pytest.param(
            {"end_time": None, "value": {"two": 2}},
            {"start_time": "2025-07-01T00:00:00+00:00", "end_time": "2025-07-01T23:59:59+00:00"},
            # the state checkpoints at `start_date` for the partition
            {
                "lookback_window": 0,
                "parent_state": {},
                "states": [
                    {"cursor": {"date": "2025-07-01T00:00:00+00:00"}, "partition": {"business_account_id": "instagram_business_account_id"}}
                ],
                "use_global_cursor": False,
            },
            id="test_no_end_time_value_in_record",
        ),
        # the state is updated to the value of `end_time`
        pytest.param(
            {"end_time": "2025-07-01T07:00:00+00:00", "value": None},
            {"start_time": "2025-07-01T00:00:00+00:00", "end_time": "2025-07-01T23:59:59+00:00"},
            {
                "lookback_window": 0,
                "state": {"date": "2025-07-01T07:00:00+00:00"},
                "states": [
                    {"cursor": {"date": "2025-07-01T07:00:00+00:00"}, "partition": {"business_account_id": "instagram_business_account_id"}}
                ],
                "use_global_cursor": False,
                "parent_state": {},
            },
            id="test_no_value_in_record",
        ),
        # the state checkpoints at `start_date` for the partition
        pytest.param(
            {"end_time": None, "value": None},
            {"start_time": "2025-07-01T00:00:00+00:00", "end_time": "2025-07-01T23:59:59+00:00"},
            {
                "lookback_window": 0,
                "parent_state": {},
                "states": [
                    {"cursor": {"date": "2025-07-01T00:00:00+00:00"}, "partition": {"business_account_id": "instagram_business_account_id"}}
                ],
                "use_global_cursor": False,
            },
            id="test_no_end_time_and_no_value_in_record",
        ),
    ],
)
@freezegun.freeze_time("2025-07-01T23:59:59Z")
def test_user_insights_state(requests_mock, values, slice_dates, expected):
    """
    This test shows how `STATE` is managed based on the scenario for Incremental Read.
    """
    logger = init_logger("airbyte")
    logger.setLevel(logging.DEBUG)

    config = {"start_date": "2025-07-01T00:00:00Z", "access_token": "unknown_token"}

    mock_accounts_request(requests_mock=requests_mock, some_config=config)
    requests_mock.register_uri(
        "GET",
        f"{GRAPH_URL}/instagram_business_account_id/insights",
        json={
            "data": [
                {
                    "description": "test_insight",
                    "id": "123",
                    "name": "test_insight_metric",
                    "period": "day",
                    "title": "Test Insight",
                    "values": [values],
                }
            ]
        },
    )

    # UserInsights stream
    stream = find_stream(stream_name="user_insights", config=config)
    for partition in stream.generate_partitions():
        for record in partition.read():
            stream.cursor.observe(record)
        stream.cursor.close_partition(partition)
    stream.cursor.ensure_at_least_one_state_emitted()
    assert stream.cursor.state == expected


@pytest.mark.parametrize(
    "error_response",
    [
        pytest.param({"json": {"error": {"type": "OAuthException", "code": 1}}}, id="test_oauth_error"),
        pytest.param({"json": {"error": {"code": 4}}}, id="test_rate_limit_error"),
        pytest.param({"json": {}, "status_code": 429}, id="test_too_many_request_error"),
        pytest.param(
            {
                "json": {"error": {"code": 1, "message": "Please reduce the amount of data you're asking for, then retry your request"}},
                "status_code": 500,
            },
            id="test_reduce_amount_of_data_error",
        ),
        pytest.param({"json": {"error": {"code": 1, "message": "An unknown error occurred"}}, "status_code": 500}, id="test_unknown_error"),
        pytest.param(
            {
                "json": {
                    "error": {"type": "OAuthException", "message": "(#10) Not enough viewers for the media to show insights", "code": 10}
                }
            },
            id="test_viewers_insights_error",
        ),
        pytest.param({"json": {"error": {"code": 100, "error_subcode": 33}}, "status_code": 400}, id="test_4028_issue_error"),
        pytest.param({"json": {"error": {"is_transient": True}}}, id="test_transient_error"),
        pytest.param({"json": {"error": {"code": 4, "error_subcode": 2108006}}}, id="test_user_media_creation_time_error"),
    ],
)
@freezegun.freeze_time("2025-07-01T23:59:59Z")
def test_common_error_retry(components_module, error_response, requests_mock, account_id, mocker):
    # The API budget's 429 handling waits on a real monotonic clock; budget throttling is not under test here
    mocker.patch.object(HttpAPIBudget, "update_from_response")
    config = {"start_date": "2025-07-01T00:00:00Z", "access_token": "unknown_token"}
    mock_accounts_request(requests_mock=requests_mock, some_config=config)
    mock_user_insights_day_request(requests_mock, {"end_time": "2025-07-01 07:00:00+0000", "value": 4}, error_response)
    mock_user_insights_requests(requests_mock, {"end_time": "2025-07-01 07:00:00+0000", "value": 4})

    stream = find_stream(stream_name="user_insights", config=config)
    records = read_full_refresh(stream)

    assert records
