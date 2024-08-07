#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

from typing import Any, Mapping
from unittest.mock import MagicMock

from airbyte_cdk.sources.streams import Stream
from pytest import fixture
from source_pinterest.reports import CampaignAnalyticsReport
from source_pinterest.source import SourcePinterest


@fixture
def test_config() -> Mapping[str, str]:
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
        "start_date": "2021-05-07",
    }


@fixture
def wrong_date_config() -> Mapping[str, str]:
    return {
        "client_id": "test_client_id",
        "client_secret": "test_client_secret",
        "refresh_token": "test_refresh_token",
        "start_date": "wrong_date_format",
    }


@fixture
def test_incremental_config() -> Mapping[str, Any]:
    return {
        "authenticator": MagicMock(),
        "start_date": "2021-05-07",
    }


@fixture
def test_current_stream_state() -> Mapping[str, str]:
    return {"updated_time": "2021-10-22"}


@fixture
def test_record() -> Mapping[str, Any]:
    return {"items": [{}], "bookmark": "string"}


@fixture
def test_record_filter() -> Mapping[str, Any]:
    return {"items": [{"updated_time": "2021-11-01"}], "bookmark": "string"}


@fixture
def test_response(test_record) -> MagicMock:
    response = MagicMock()
    response.json.return_value = test_record
    return response


@fixture
def analytics_report_stream() -> CampaignAnalyticsReport:
    return CampaignAnalyticsReport(parent=None, config=MagicMock())


@fixture
def date_range() -> Mapping[str, Any]:
    return {"start_date": "2023-01-01", "end_date": "2023-01-31", "parent": {"id": "123"}}


@fixture(autouse=True)
def mock_auth(requests_mock) -> None:
    requests_mock.post(
        url="https://api.pinterest.com/v5/oauth/token",
        json={"access_token": "access_token", "expires_in": 3600},
    )


def get_stream_by_name(stream_name: str, config: Mapping[str, Any]) -> Stream:
    source = SourcePinterest()
    matches_by_name = [stream_config for stream_config in source.streams(config) if stream_config.name == stream_name]
    if not matches_by_name:
        raise ValueError("Please provide a valid stream name.")
    return matches_by_name[0]
