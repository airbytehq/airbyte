#
# Copyright (c) 2023 Airbyte, Inc., all rights reserved.
#

import json
from unittest.mock import MagicMock

import pytest
from airbyte_cdk.models import ConnectorSpecification
from source_tiktok_marketing import SourceTiktokMarketing

SANDBOX_CONFIG_FILE = "secrets/sandbox_config.json"
PROD_CONFIG_FILE = "secrets/prod_config.json"
PROD_LIFETIME_CONFIG_FILE = "secrets/prod_config_with_lifetime_granularity.json"
PROD_DAILY_CONFIG_FILE = "secrets/prod_config_with_day_granularity.json"


@pytest.mark.parametrize(
    "config, stream_len",
    [
        (PROD_CONFIG_FILE, 36),
        (SANDBOX_CONFIG_FILE, 28),
        (PROD_LIFETIME_CONFIG_FILE, 15),
        (PROD_DAILY_CONFIG_FILE, 27),
    ],
)
def test_source_streams(config, stream_len):
    with open(config) as f:
        config = json.load(f)
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

