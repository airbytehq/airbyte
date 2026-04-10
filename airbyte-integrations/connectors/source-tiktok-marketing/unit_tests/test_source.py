#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pytest

from airbyte_cdk.models import ConnectorSpecification, Status

from .conftest import get_source

EXPECTED_REPORT_PRIMARY_KEYS = {
    "ads_reports_daily": [["advertiser_id"], ["ad_id"], ["stat_time_day"]],
    "ads_reports_by_country_daily": [["advertiser_id"], ["ad_id"], ["stat_time_day"], ["country_code"]],
    "ad_groups_reports_daily": [["advertiser_id"], ["adgroup_id"], ["stat_time_day"]],
    "ad_groups_reports_by_country_daily": [["advertiser_id"], ["adgroup_id"], ["stat_time_day"], ["country_code"]],
    "advertisers_reports_daily": [["advertiser_id"], ["stat_time_day"]],
    "campaigns_reports_daily": [["advertiser_id"], ["campaign_id"], ["stat_time_day"]],
    "campaigns_audience_reports_daily": [["advertiser_id"], ["campaign_id"], ["stat_time_day"], ["gender"], ["age"]],
    "ad_group_audience_reports_daily": [["advertiser_id"], ["adgroup_id"], ["stat_time_day"], ["gender"], ["age"]],
    "ads_audience_reports_daily": [["advertiser_id"], ["ad_id"], ["stat_time_day"], ["gender"], ["age"]],
    "advertisers_audience_reports_daily": [["advertiser_id"], ["stat_time_day"], ["gender"], ["age"]],
    "campaigns_audience_reports_by_country_daily": [["advertiser_id"], ["campaign_id"], ["stat_time_day"], ["country_code"]],
    "ad_group_audience_reports_by_country_daily": [["advertiser_id"], ["adgroup_id"], ["stat_time_day"], ["country_code"]],
    "ads_audience_reports_by_country_daily": [["advertiser_id"], ["ad_id"], ["stat_time_day"], ["country_code"]],
    "advertisers_audience_reports_by_country_daily": [["advertiser_id"], ["stat_time_day"], ["country_code"]],
    "campaigns_audience_reports_by_platform_daily": [["advertiser_id"], ["campaign_id"], ["stat_time_day"], ["platform"]],
    "ad_group_audience_reports_by_platform_daily": [["advertiser_id"], ["adgroup_id"], ["stat_time_day"], ["platform"]],
    "ads_audience_reports_by_platform_daily": [["advertiser_id"], ["ad_id"], ["stat_time_day"], ["platform"]],
    "advertisers_audience_reports_by_platform_daily": [["advertiser_id"], ["stat_time_day"], ["platform"]],
    "ads_audience_reports_by_province_daily": [["advertiser_id"], ["ad_id"], ["stat_time_day"], ["province_id"]],
    "ads_reports_hourly": [["advertiser_id"], ["ad_id"], ["stat_time_hour"]],
    "ads_reports_by_country_hourly": [["advertiser_id"], ["ad_id"], ["stat_time_hour"], ["country_code"]],
    "advertisers_reports_hourly": [["advertiser_id"], ["stat_time_hour"]],
    "campaigns_reports_hourly": [["advertiser_id"], ["campaign_id"], ["stat_time_hour"]],
    "ad_groups_reports_hourly": [["advertiser_id"], ["adgroup_id"], ["stat_time_hour"]],
    "ad_groups_reports_by_country_hourly": [["advertiser_id"], ["adgroup_id"], ["stat_time_hour"], ["country_code"]],
    "ads_reports_lifetime": [["advertiser_id"], ["ad_id"]],
    "advertisers_reports_lifetime": [["advertiser_id"]],
    "campaigns_reports_lifetime": [["advertiser_id"], ["campaign_id"]],
    "ad_groups_reports_lifetime": [["advertiser_id"], ["adgroup_id"]],
    "advertisers_audience_reports_lifetime": [["advertiser_id"], ["gender"], ["age"]],
}


@pytest.mark.parametrize(
    "config, stream_len",
    [
        ({"access_token": "token", "environment": {"app_id": "1111", "secret": "secret"}, "start_date": "2021-04-01"}, 44),
        ({"access_token": "token", "start_date": "2021-01-01", "environment": {"advertiser_id": "1111"}}, 28),
        (
            {
                "access_token": "token",
                "environment": {"app_id": "1111", "secret": "secret"},
                "start_date": "2021-04-01",
                "report_granularity": "LIFETIME",
            },
            44,
        ),
        (
            {
                "access_token": "token",
                "environment": {"app_id": "1111", "secret": "secret"},
                "start_date": "2021-04-01",
                "report_granularity": "DAY",
            },
            44,
        ),
    ],
)
def test_source_streams(config, stream_len):
    streams = get_source(config=config, state=None).streams(config=config)
    assert len(streams) == stream_len


def test_report_stream_primary_keys():
    config = {"access_token": "token", "environment": {"app_id": "1111", "secret": "secret"}, "start_date": "2021-04-01"}

    discovered_catalog = get_source(config=config, state=None).discover(logger=None, config=config)
    stream_primary_keys = {stream.name: stream.source_defined_primary_key for stream in discovered_catalog.streams}

    assert {name: stream_primary_keys[name] for name in EXPECTED_REPORT_PRIMARY_KEYS} == EXPECTED_REPORT_PRIMARY_KEYS


def test_source_spec(config):
    spec = get_source(config=config, state=None).spec(logger=None)
    assert isinstance(spec, ConnectorSpecification)


@pytest.fixture(name="config")
def config_fixture():
    config = {
        "account_id": 123,
        "access_token": "TOKEN",
        "start_date": "2019-10-10T00:00:00",
        "end_date": "2020-10-10T00:00:00",
    }
    return config


def test_source_check_connection_ok(config, requests_mock):
    requests_mock.get(
        "https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/",
        json={
            "code": 0,
            "message": "ok",
            "data": {
                "list": [
                    {"advertiser_id": "917429327", "advertiser_name": "name"},
                ]
            },
        },
    )
    requests_mock.get(
        "https://business-api.tiktok.com/open_api/v1.3/advertiser/info/?page_size=100&advertiser_ids=%5B%22917429327%22%5D",
        json={
            "code": 0,
            "message": "ok",
            "data": {
                "list": [
                    {"advertiser_id": "917429327", "advertiser_name": "name"},
                ]
            },
        },
    )
    logger_mock = MagicMock()
    assert get_source(config=config, state=None).check(logger_mock, config).status == Status.SUCCEEDED


@pytest.mark.parametrize(
    "json_response, expected_result, expected_message",
    [
        (
            {"code": 40105, "message": "Access token is incorrect or has been revoked."},
            (Status.FAILED, "Stream advertisers is not available: Access token is incorrect or has been revoked."),
            None,
        ),
        ({"code": 40100, "message": "App reaches the QPS limit."}, None, 6),
    ],
)
@pytest.mark.usefixtures("mock_sleep")
def test_source_check_connection_failed(config, requests_mock, capsys, json_response, expected_result, expected_message):
    requests_mock.get("https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/", json=json_response)
    requests_mock.get(
        "https://business-api.tiktok.com/open_api/v1.3/advertiser/info/?page_size=100&advertiser_ids=%5B%22917429327%22%5D",
        json=json_response,
    )

    logger_mock = MagicMock()
    result = get_source(config=config, state=None).check(logger_mock, config)

    if expected_result is not None:
        assert result.status == expected_result[0]
        assert expected_result[1] in result.message
    if expected_message is not None:
        trace_messages = capsys.readouterr().out.split()
        assert len(trace_messages) == expected_message
