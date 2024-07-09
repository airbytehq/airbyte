#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import ConnectorSpecification
from source_tiktok_marketing import SourceTiktokMarketing


@pytest.mark.parametrize(
    "config, stream_len",
    [
        ({"access_token": "token", "environment": {"app_id": "1111", "secret": "secret"}, "start_date": "2021-04-01"}, 36),
        ({"access_token": "token", "start_date": "2021-01-01", "environment": {"advertiser_id": "1111"}}, 28),
        ({"access_token": "token", "environment": {"app_id": "1111", "secret": "secret"}, "start_date": "2021-04-01", "report_granularity": "LIFETIME"}, 15),
        ({"access_token": "token", "environment": {"app_id": "1111", "secret": "secret"}, "start_date": "2021-04-01", "report_granularity": "DAY"}, 27),
    ],
)
def test_source_streams(config, stream_len):
    streams = SourceTiktokMarketing().streams(config=config)
    assert len(streams) == stream_len


def test_source_spec():
    spec = SourceTiktokMarketing().spec(logger=None)
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
        json={"code": 0, "message": "ok", "data": {"list": [{"advertiser_id": "917429327", "advertiser_name": "name"}, ]}}
    )
    requests_mock.get(
        "https://business-api.tiktok.com/open_api/v1.3/advertiser/info/?page_size=100&advertiser_ids=%5B%22917429327%22%5D",
        json={"code": 0, "message": "ok", "data": {"list": [{"advertiser_id": "917429327", "advertiser_name": "name"}, ]}}
    )
    logger_mock = MagicMock()
    assert SourceTiktokMarketing().check_connection(logger_mock, config) == (True, None)


def test_source_check_connection_failed(config, requests_mock):
    requests_mock.get(
        "https://business-api.tiktok.com/open_api/v1.3/oauth2/advertiser/get/",
        json={"code": 40105, "message": "Access token is incorrect or has been revoked."}
    )
    logger_mock = MagicMock()
    assert SourceTiktokMarketing().check_connection(logger_mock, config) == (
        False, "Unable to connect to stream advertisers - Access token is incorrect or has been revoked."
    )

